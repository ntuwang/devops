# -*- coding: utf-8 -*-
# @Time    : 17-8-17 下午2:35
# @Author  : Wang Chao

import jenkins
import time
from django.conf import settings


class JenkinsJob(object):
    def __init__(self, username, password, jobname):
        self.username = username
        self.password = password
        self.jobname = jobname
        self.server = jenkins.Jenkins(settings.JENKINSURL, username=self.username, password=self.password)

    def jobbuild(self):
        server = self.server
        jobname = self.jobname
        last_build_number = int(server.get_job_info(jobname)['lastCompletedBuild']['number'])
        server.build_job(jobname)
        this_build_number = int(server.get_job_info(jobname)['lastCompletedBuild']['number'])
        while not this_build_number == (last_build_number + 1):
            this_build_number = int(server.get_job_info(jobname)['lastCompletedBuild']['number'])
            time.sleep(10)
        jobresult = server.get_build_info(jobname, this_build_number)[u'result']
        mydict = {}
        mydict['result'] = jobresult
        mydict['num'] = this_build_number
        return mydict

    def job_console(self,num):
        output = self.server.get_build_console_output(self.jobname, num)
        return output


if __name__ == '__main__':
    a = JenkinsJob(username="xxxxx", password="xxxxx", jobname='test-hello')
    a.jobbuild()
