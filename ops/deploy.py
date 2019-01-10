# -*- coding: utf-8 -*-
# @Time    : 17-8-17 上午9:14
# @Author  : Wang Chao

import os
import threading
from .models import Deploys
import fnmatch
from django.conf import settings
from utils.fabfile import Fabapi
from utils.jenkinsjob import JenkinsJob
import base64
import time
import traceback



def deploy_thread(project_id, deploy_id, deploys):
    deploy = Deploys.objects.filter(id=deploy_id).get()

    jenkinsip = settings.JENKINSIP
    jenkinsjob = deploy.project.jenkins_name
    jenkinsworkspace = os.path.join(settings.JENKINSBASEPATH, '{0}.{1}'.format(deploy.branch, jenkinsjob))

    localws = os.path.join(deploy.project.local_dir, 'qa/')

    if deploy.status != 3:
        return
    try:
        deploys.update(deploy, progress=0, status=2)

        # =======before checkout========
        cmd = "mkdir -p {local_dir} && cd {local_dir} && rm -rf {local_dir}/*.war {local_dir}/*.jar".format(
            local_dir=localws)
        f = Fabapi(hostip=jenkinsip)
        f.remoted(cmd)
        deploys.update(deploy, progress=5, status=2)
        deploys.append_comment(deploy, "Jenkins 任务：\n--任务名称:{0},git分支:{1}\n".format(jenkinsjob, deploy.branch))

        # ======== Jenkins ========
        if deploy.jenkinsbd.strip() == 'yes':
            deploys.append_comment(deploy, "--拉取代码并编译打包（by git and maven）\n")
            jenkins = JenkinsJob(username=settings.JENKINSUSER, password=base64.b64decode(settings.JENKINSPASS),
                                 jobname='{0}.{1}'.format(deploy.branch, jenkinsjob))
            j = jenkins.jobbuild()
            result = j['result']
            num = int(j['num'])
            if not result == 'SUCCESS':
                deploys.append_comment(deploy, "--Jenkins 构建失败\n\n")
                raise Exception("Jenkins")
            else:
                deploys.append_comment(deploy,
                                       "--Jenkins 构建成功\n"
                                       "--任务日志请访问:/deploy/code/jenkins/?jobname={0}.{1}&&num={2}\n\n".format(
                                           deploy.branch, jenkinsjob, num))
        else:
            deploys.append_comment(deploy, "--Jenkins 任务本次不执行构建\n\n")
        deploys.update(deploy, progress=15, status=2)

        deploys.append_comment(deploy, "开始部署:\n")
        # ========= checkouting ==========
        deploys.append_comment(deploy, "检出应用程序包。。。\n")
        time.sleep(1)

        # ========= copy wars to local ============
        for warnames in deploy.warnames.strip().split(','):
            cmd = "find {jenkinsworkspace} -iname {warnames} | xargs ls -lta | awk '{{print $NF}}' | head -n 1".format(
                jenkinsworkspace=jenkinsworkspace,
                warnames=warnames)

            warpath = f.remoted(cmd)
            print(warpath)
            time.sleep(1)
            f.getfile(local_dest=localws, remote_dest=warpath)
            # execute(jenkinsfab.getfile, local_dest=localws, remote_dest=warpath)
            deploys.append_comment(deploy, "程序包下载完成\n".format(warnames))

        deploys.update(deploy, progress=45, status=2)

        # =========== before deploy  =================
        hostfab = Fabapi(hostip=deploy.host.public_ip)
        deploys.append_comment(deploy, "准备部署 目标主机： {0}\n".format(deploy.host.public_ip))
        cmd = ("mkdir -p {remote_history_dir} && chmod -R 777 {remote_history_dir}".format(
            remote_history_dir=os.path.join(deploy.project.remote_history_dir,
                                            deploy.created_at.strftime('%Y%m%d-%H%M%S'))))
        hostfab.remoted(cmd)
        # execute(hostfab.remoted, rd=cmd, sudoif=1)

        deploys.append_comment(deploy, "--删除过期的历史备份\n")
        cmd = ("WORKSPACE='{0}' && cd $WORKSPACE && ls -1t | tail -n +{1} | xargs rm -rf".format(
            deploy.project.remote_history_dir, settings.MAX_DEPLOY_HISTORY))
        hostfab.remoted(cmd)
        # execute(hostfab.remoted, rd=cmd, sudoif=1)
        before_deploy = deploy.project.before_deploy.replace("\r", "").replace("\n", " && ")
        # ========== create dest dirs ===================

        cmd = ("mkdir -p {destwar_dir} ".format(destwar_dir=deploy.project.destwar_dir))
        hostfab.remoted(cmd)
        # execute(hostfab.remoted, rd=cmd, sudoif=1)
        if before_deploy:
            cmd = before_deploy
            hostfab.remoted(cmd)
            deploys.append_comment(deploy, "暂停tomcat应用\n--exec {0}\n".format(cmd))
            # execute(hostfab.remoted, rd=cmd, sudoif=1)

        deploys.update(deploy, progress=67, status=2)

        if deploy.project.destwar_dir.replace("\r", "").replace("\n", ""):
            for war_name in deploy.warnames.strip().split(','):
                app_name = war_name.split('.')[0]
                if app_name:
                    try:
                        cmd = (
                            "mv {destwar_dir}/{war_name} {remote_history_dir} ; rm -rf {destwar_dir}/{app_name} ".format(
                                destwar_dir=deploy.project.destwar_dir,
                                war_name=war_name,
                                app_name=app_name,
                                remote_history_dir=os.path.join(deploy.project.remote_history_dir,
                                                                deploy.created_at.strftime('%Y%m%d-%H%M%S'))))

                        deploys.append_comment(deploy, "--执行本次备份\n")
                        hostfab.remoted(cmd)
                        # execute(hostfab.remoted, rd=cmd, sudoif=1)
                        deploys.append_comment(deploy, "--部署新版本应用包\n")
                        hostfab.putfile(local_dest="%s/%s" % (localws, war_name),
                                        remote_dest=deploy.project.destwar_dir)
                        # execute(hostfab.putfile, local_dest="%s/%s" % (localws, war_name),
                        #         remote_dest=deploy.project.destwar_dir)
                    except BaseException as e:
                        print(e)
                else:
                    raise  Exception("project not exists")

        deploys.append_comment(deploy, "部署完成!\n")
        deploys.update(deploy, progress=83, status=2)

        # =============== after deploy =============
        deploys.append_comment(deploy, "启动服务并将康检查\n")

        after_deploy = deploy.project.after_deploy.replace("\r", "").replace(
            "\n", " && ")
        if after_deploy:
            cmd = after_deploy
            deploys.append_comment(deploy, "--exec {0}\n".format(cmd))
            f.remoted(cmd)
            time.sleep(10)
        deploys.append_comment(deploy, "应用启动正常\n")
        deploys.append_comment(deploy, "完成,结束!\n")

    except BaseException as err:
        traceback.print_exc()

        deploys.append_comment(deploy, repr(err))
        deploys.update(deploy, progress=100, status=0)
    else:
        deploys.update(deploy, progress=100, status=1)
    finally:

        deploy = deploys.first(id=deploy_id)
        if deploy:
            deploys.deploy(deploy)


def rollback_thread(project_id, deploy_id, deploys):
    deploy = Deploys.objects.filter(id=deploy_id).get()
    deploy.comment = ''
    deploy.save()
    if deploy.status != 1:
        deploys.append_comment(deploy, "该次部署不成功，不能回滚\n")

    try:
        # before rollback
        deploys.append_comment(deploy, "检查备份文件(at {0})\n".format(deploy.created_at.strftime('%Y%m%d-%H%M%S')))
        f = Fabapi(hostip=deploy.host.public_ip)
        apppath = os.path.join(deploy.project.remote_history_dir, deploy.created_at.strftime('%Y%m%d-%H%M%S'),
                               deploy.warnames)
        cmd = '[ -f {0} ] && echo 0 || echo 1 | head -n 1'.format(apppath)

        res = f.remoted(cmd)

        if res != '0':
            deploys.append_comment(deploy, "备份文件不存在，回滚终止\n")
            raise Exception("备份文件不存在，回滚终止")

        deploys.append_comment(deploy, "备份文件存在，回滚开始\n")
        deploys.update(deploy, progress=33, status=2)
        # rollback

        cmd = (
            "rm -rf {destwar_dir}/{war_name} ; rm -rf {destwar_dir}/{app_name} ".format(
                destwar_dir=deploy.project.destwar_dir,
                war_name=deploy.warnames,
                app_name=deploy.warnames.split('.')[0]))

        f.remoted(cmd)
        deploys.append_comment(deploy, "---清空旧数据\n")
        deploys.update(deploy, progress=67, status=2)

        cmd = (
            "cp -rp {apppath} {destwar_dir}".format(apppath=apppath, destwar_dir=deploy.project.destwar_dir)
        )
        f.remoted(cmd)
        deploys.append_comment(deploy, "---恢复文件完成\n")

        # after rollback
        # =============== after deploy =============
        deploys.append_comment(deploy, "启动服务并将康检查\n")
        after_deploy = deploy.project.after_deploy.replace("\r", "").replace(
            "\n", " && ")
        if after_deploy:
            cmd = after_deploy
            deploys.append_comment(deploy, "exec {0}\n".format(cmd))
            f.remoted(cmd)
            time.sleep(10)
        deploys.append_comment(deploy, "应用启动正常\n")
        deploys.append_comment(deploy, "回滚完成,结束!\n")
        deploys.update(deploy, progress=100, status=4)

    except Exception as err:
        traceback.print_exc()
        deploys.append_comment(deploy, repr(err))
        deploys.update(deploy, progress=100, status=5)
    else:
        deploys.update(deploy, progress=100, status=1)
    finally:

        deploy = deploys.first(id=deploy_id)
        if deploy:
            deploys.deploy(deploy)


def iterfindfiles(path, fnexp):
    for root, dirs, files in os.walk(path):
        for warfile in fnmatch.filter(files, fnexp):
            yield os.path.join(root, warfile)


class DeploysService(object):
    def first(self, **kargs):
        # 返回一个object
        return Deploys.objects.filter(**kargs).get()

    def update(self, deploy, progress, status):
        deploy.progress = progress
        deploy.status = status
        deploy.save()

    def deploy(self, deploy):
        t = threading.Thread(target=deploy_thread,
                             args=(deploy.project_id, deploy.id, deploys),
                             name="pydelo-deploy[%d]" % deploy.id)
        t.start()

    def rollback(self, deploy):
        t = threading.Thread(target=rollback_thread,
                             args=(deploy.project_id, deploy.id, deploys),
                             name="pydelo-rollback[%d]" % deploy.id)
        t.start()

    def append_comment(self, deploy, comment):
        if deploy.comment:
            deploy.comment = str(deploy.comment) + comment
        else:
            deploy.comment = comment
        deploy.save()
        return deploy


deploys = DeploysService()
rundeploys = DeploysService()
