# -*- coding: utf-8 -*-
# @Time    : 17-8-17 上午9:14
# @Author  : Wang Chao

import os
import threading
from .models import Deploys
import fnmatch
from django.conf import settings
from utils.jenkins_job import JenkinsJob
import time
import traceback
import base64
from utils.config_parser import ConfParserClass
from utils.saltapi import SaltApi
from urllib.parse import urljoin


def deploy_thread(deploy_id):

    deploy_service = DeploysService(deploy_id)
    deploy = Deploys.objects.get(pk=deploy_id)

    cp = ConfParserClass('conf/settings.conf')
    salt_url = cp.get('saltstack', 'url')
    salt_username = cp.get('saltstack', 'username')
    salt_password = cp.get('saltstack', 'password')

    sapi = SaltApi(url=salt_url, username=salt_username, password=salt_password)

    if deploy.status != 3:
        return
    try:
        deploy_service.update_deploy(progress=0, status=2)
        deploy_service.append_comment("开始部署:\n")

        time.sleep(3)
        # ========= checkouting ==========
        deploy_service.update_deploy(progress=10, status=2)
        deploy_service.append_comment("检出应用程序包。。。\n")
        url = urljoin(settings.NG_FILE_BASE,deploy.project.name,deploy.version)
        url = urljoin(url,deploy.pkg_name)
        time.sleep(1)
        sapi.remote_execution('*', 'cmd.run',
                              'wget {0} -o {1}'.format(url,deploy.project.target_path))
        time.sleep(8)
        deploy_service.append_comment("下载完成\n")
        deploy_service.update_deploy(progress=15, status=2)

        # =========== before deploy  =================
        deploy_service.append_comment("准备部署 目标主机： {0}\n".format(deploy.host.public_ip))
        cmd = ("mkdir -p {remote_history_dir} && chmod -R 777 {remote_history_dir}".format(
            remote_history_dir=os.path.join(deploy.project.remote_history_dir,
                                            deploy.created_at.strftime('%Y%m%d-%H%M%S'))))

        # execute(hostfab.remoted, rd=cmd, sudoif=1)
        sapi.remote_execution(deploy.host.public_ip, 'cmd.run', cmd)
        deploy_service.append_comment("--删除过期的历史备份\n")
        cmd = ("WORKSPACE='{0}' && cd $WORKSPACE && ls -1t | tail -n +{1} | xargs rm -rf".format(
            deploy.project.remote_history_dir, cp.get('deploy', 'backup_count')))
        sapi.remote_execution(deploy.host.public_ip, 'cmd.run', cmd)
        time.sleep(8)
        # ========== create dest dirs ===================

        cmd = ("mkdir -p {dest_path} ".format(dest_path=deploy.project.deploy_path))
        sapi.remote_execution(deploy.host.public_ip, 'cmd.run', cmd)
        # execute(hostfab.remoted, rd=cmd, sudoif=1)

        deploy_service.append_comment("部署结束!\n")
        deploy_service.update_deploy(progress=83, status=2)
        time.sleep(8)
        # =============== after deploy =============
        deploy_service.append_comment("启动服务并将康检查\n")
        deploy_service.append_comment("应用启动正常\n")
        deploy_service.append_comment("完成,结束!\n")

    except BaseException as err:
        traceback.print_exc()

        deploy_service.append_comment(repr(err))
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
                             args=(self.deploy_id,),
                             name="pydelo-deploy[%d]" % self.deploy.id)

        t.start()

    def append_comment(self, comment):
        if self.deploy.comment:
            self.deploy.comment = str(self.deploy.comment) + comment
        else:
            self.deploy.comment = comment
        self.deploy.save()
        return self.deploy
