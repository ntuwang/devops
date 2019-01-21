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
import time
import traceback
import base64
from utils.config_parser import Conf_Parser
from utils.saltapi import SaltApi


def deploy_thread(deploy):
    cp = Conf_Parser('conf/settings.conf')
    deploy_service = DeploysService(deploy.id)
    jenkins_ip = cp.get('jenkins', 'url')
    jenkins_job = deploy.project.jenkins_name
    jenkins_user = cp.get('jenkins', 'user')
    jenkins_pass = base64.b64decode(cp.get('jenkins', 'pass'))
    salt_url = cp.get('saltstack', 'url')
    salt_username = cp.get('saltstack', 'username')
    salt_password = cp.get('saltstack', 'password')

    sapi = SaltApi(url=salt_url, username=salt_username, password=salt_password)


    if deploy.status != 3:
        return
    try:
        deploy_service.update_deploy(progress=0, status=2)

        # =======before checkout========
        deploy_service.update_deploy(progress=5, status=2)
        deploy_service.append_comment( "Jenkins 任务：\n--任务名称:{0},git分支:{1}\n".format(jenkins_job, deploy.branch))

        # ======== Jenkins ========
        if deploy.jenkinsbd.strip() == 'yes':
            deploy_service.append_comment( "--拉取代码并编译打包（by git and maven）\n")
            jenkins = JenkinsJob(username=jenkins_user, password=jenkins_pass,
                                 jobname='{0}.{1}'.format(deploy.branch, jenkins_job))
            j = jenkins.jobbuild()
            result = j['result']
            num = int(j['num'])
            if not result == 'SUCCESS':
                deploy_service.append_comment( "--Jenkins 构建失败\n\n")
                raise Exception("Jenkins")
            else:
                deploy_service.append_comment(
                                              "--Jenkins 构建成功\n"
                                              "--任务日志请访问:/deploy/code/jenkins/?jobname={0}.{1}&&num={2}\n\n".format(
                                                  deploy.branch, jenkins_job, num))
        else:
            deploy_service.append_comment( "--Jenkins 任务本次不执行构建\n\n")
        deploy_service.update_deploy(progress=15, status=2)

        deploy_service.append_comment( "开始部署:\n")
        # ========= checkouting ==========
        deploy_service.append_comment( "检出应用程序包。。。\n")
        time.sleep(1)
        sapi.remote_execution('*', 'cmd.run', 'wget http://devops-wctest.chinacloudapp.cn/file_download_manage/test01.war -o /root/test01.war')

        # =========== before deploy  =================
        hostfab = Fabapi(hostip=deploy.host.public_ip)
        deploy_service.append_comment( "准备部署 目标主机： {0}\n".format(deploy.host.public_ip))
        cmd = ("mkdir -p {remote_history_dir} && chmod -R 777 {remote_history_dir}".format(
            remote_history_dir=os.path.join(deploy.project.remote_history_dir,
                                            deploy.created_at.strftime('%Y%m%d-%H%M%S'))))
        hostfab.remoted(cmd)
        # execute(hostfab.remoted, rd=cmd, sudoif=1)

        deploy_service.append_comment( "--删除过期的历史备份\n")
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
            deploy_service.append_comment( "暂停tomcat应用\n--exec {0}\n".format(cmd))
            # execute(hostfab.remoted, rd=cmd, sudoif=1)

        deploy_service.update_deploy(progress=67, status=2)

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

                        deploy_service.append_comment( "--执行本次备份\n")
                        hostfab.remoted(cmd)
                        # execute(hostfab.remoted, rd=cmd, sudoif=1)
                        deploy_service.append_comment( "--部署新版本应用包\n")

                        # execute(hostfab.putfile, local_dest="%s/%s" % (localws, war_name),
                        #         remote_dest=deploy.project.destwar_dir)
                    except BaseException as e:
                        print(e)
                else:
                    raise Exception("project not exists")

        deploy_service.append_comment( "部署完成!\n")
        deploy_service.update_deploy(progress=83, status=2)

        # =============== after deploy =============
        deploy_service.append_comment( "启动服务并将康检查\n")

        after_deploy = deploy.project.after_deploy.replace("\r", "").replace(
            "\n", " && ")
        if after_deploy:
            cmd = after_deploy
            deploy_service.append_comment( "--exec {0}\n".format(cmd))

            time.sleep(10)
        deploy_service.append_comment( "应用启动正常\n")
        deploy_service.append_comment( "完成,结束!\n")

    except BaseException as err:
        traceback.print_exc()

        deploy_service.append_comment( repr(err))
        deploy_service.update_deploy(progress=100, status=0)
    else:
        deploy_service.update_deploy(progress=100, status=1)
    finally:
        if deploy_service:
            deploy_service.start_deploy()


def iterfindfiles(path, fnexp):
    for root, dirs, files in os.walk(path):
        for warfile in fnmatch.filter(files, fnexp):
            yield os.path.join(root, warfile)


class DeploysService(object):

    def __init__(self, deploy_id):
        self.deploy_id = deploy_id
        self.deploy = Deploys.objects.get(pk=deploy_id)

    def update_deploy(self, progress, status):
        self.deploy.progress = progress
        self.deploy.status = status
        self.deploy.save()

    def start_deploy(self, ):
        t = threading.Thread(target=deploy_thread,
                             args=(self.deploy,),
                             name="pydelo-deploy[%d]" % self.deploy.id)

        t.start()

    def append_comment(self, comment):
        if self.deploy.comment:
            self.deploy.comment = str(self.deploy.comment) + comment
        else:
            self.deploy.comment = comment
        self.deploy.save()
        return self.deploy
