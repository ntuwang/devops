# -*- coding: utf-8 -*-
# @Time    : 17-8-17 下午2:33
# @Author  : Wang Chao

from fabric import Connection

from django.conf import settings


class Fabapi(object):
    def __init__(self, hostip):
        connect_kwargs = {'pkey':settings.DEPLOYKEY,
                          # 'password':''
                          }
        self.c = Connection(host=hostip, user=settings.DEPLOYUSER, port=22,**connect_kwargs)

    def locald(self, ld):
        return self.c.local(ld)

    def remoted(self, rd, sudoif=0):
        # if sudoif == 1:
        #     return sudo(rd, pty=False)
        # else:
        #     return run(rd)
        return self.c.run(rd,pty=False,shell=False)

    def getfile(self, local_dest, remote_dest):
        self.c.get(remote_dest, local_dest)

    def putfile(self, local_dest, remote_dest):
        self.c.put(local_dest, remote_dest, mode=0o664)

    def isexists(self, rootdir):
        res = int(self.c.run(" [ -e {0} ] && echo 1 || echo 0".format(rootdir),shell=False))
        return res
