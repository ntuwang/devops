# -*- coding: utf-8 -*-
# @Time    : 17-8-17 下午2:35
# @Author  : Wang Chao

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.build import Build
import traceback
from datetime import datetime,timezone,timedelta


class JenkinsJob(object):
    def __init__(self, url, username, password):
        self.server = Jenkins(url, username=username, password=password)

    def job_build(self, job_name):
        params = {'Branch': 'oriin/master', 'host': '192.168.1.100'}
        ret = self.server.build_job(job_name, params)
        return ret

    def job_query(self, job_name):
        try:
            job = self.server.get_job(job_name)
            last_build = job.get_last_stable_build()
            build_num = last_build.get_number()
            build_status = last_build.get_status()
            tzutc_8 = timezone(timedelta(hours=8))
            build_time = last_build.get_timestamp()
            build_time = build_time.astimezone(tzutc_8).strftime('%Y-%m-%d %H:%M:%S')
            build_duration = last_build.get_duration().total_seconds()
            ret = {
                'job_name': job_name,
                'build_num': build_num,
                'build_status': build_status,
                'build_time': build_time,
                'build_duration': build_duration
            }

        except Exception:
            traceback.print_exc()
            ret = {}
        return ret

    def job_console(self, job_name):
        job = self.server.get_job(job_name)
        last_build = job.get_last_stable_build()
        ret = last_build.get_console()
        return ret

    def job_list(self):
        ret = self.server.get_jobs_list()
        return ret


if __name__ == '__main__':
    pass
