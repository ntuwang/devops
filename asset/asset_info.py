#!/usr/bin/env python
# coding: utf8
# @Time    : 17-8-11 上午11:16
# @Author  : Wang Chao

from utils.saltapi import SaltApi
import threading
from utils.config_parser import Conf_Parser

asset_info = []


cps = Conf_Parser('conf/settings.conf')
sapi = SaltApi(url=cps.get('saltstack', 'url'), username=cps.get('saltstack', 'username'),
               password=cps.get('saltstack', 'password'))


def GetInfoDict(r, arg):
    try:
        result = ''
        for k in r[arg]:
            result = result + k + ': ' + str(r[arg][k]) + '\n'
    except:
        result = 'Nan'
    return result

def GetInfo(r, arg):
    try:
        arg = str(r[arg])
    except:
        arg = 'Nan'
    return arg

def GetAssetInfo(tgt):
    '''
    Salt API获取主机信息并进行格式化输出
    '''
    global asset_info
    info = {}

    ret = sapi.remote_server_info(tgt, 'grains.items')
    info['sn']=GetInfo(ret,'serialnumber')
    info['hostname']=GetInfo(ret,'host')
    info['nodename']=tgt
    info['os']=GetInfo(ret,'os')+GetInfo(ret,'osrelease')+' '+GetInfo(ret,'osarch')
    info['manufacturer']=GetInfo(ret,'manufacturer')
    info['cpu_model']=GetInfo(ret,'cpu_model')
    info['productname']=GetInfo(ret,'productname')
    info['cpu_nums']=GetInfo(ret,'num_cpus')
    info['kernel'] = GetInfo(ret,'kernel') + GetInfo(ret,'kernelrelease')
    info['zmqversion'] = GetInfo(ret,'zmqversion')
    info['shell'] = GetInfo(ret,'shell')
    info['saltversion'] = GetInfo(ret,'saltversion')
    info['locale'] = GetInfoDict(ret, 'locale_info')
    info['selinux'] = GetInfoDict(ret, 'selinux')

    if 'virtual_subtype' in ret:
        virtual = GetInfo(ret,'virtual') + '-' + GetInfo(ret,'virtual_subtype')
    else:
        virtual=GetInfo(ret,'virtual')
    info['virtual'] = virtual

    try:
        hwaddr = ret['hwaddr_interfaces']
        ipaddr = ret['ip4_interfaces']
        hwaddr.pop('lo')
        ipaddr.pop('lo')
        network = ''
        for i in ipaddr:
            ip = ''
            for j in ipaddr[i]:
                ip = ip + j + '/'
            network = network + i + ': ' + ip.strip('/') + '-' + hwaddr[i] + '\n'
        info['network'] =  network
    except:
        info['network'] = 'Nan'

    mem=GetInfo(ret,'mem_total')
    if int(mem) > 1000:
        mem = int(mem)/1000.0
        memory = ('%.1f'%mem) + 'G'
    else:
        memory = str(mem) + 'M'
    info['memory'] = memory

    ret = sapi.remote_server_info(tgt, 'disk.usage')
    disk = ''
    for i in ret:
        r = int(ret[i]['1K-blocks'])/1000
        if r > 1000:
            r = r/1000
            s = str(r) + 'G'
            if r > 1000:
                r = r/1000.0
                s = ('%.1f'%r) + 'T'
        else:
            s = str(r) + 'M'
        disk = disk + i + ': ' + s + '\n'
    info['disk'] = disk

    asset_info.append(info)


def MultipleCollect(tgt_list):
    global asset_info
    asset_info = []
    threads = []
    loop = 0
    count = len(tgt_list)
    for i in range(0, count, 2):
        keys = range(loop*2, (loop+1)*2, 1)

        #实例化线程
        for i in keys:
            if i >= count:
                break
            else:
                t = threading.Thread(target=GetAssetInfo, args=(tgt_list[i],))
                threads.append(t)
        #启动线程
        for i in keys:
            if i >=count:
                break
            else:
                threads[i].start()
        #等待并发线程结束
        for i in keys:
            if i >= count:
                break
            else:
                threads[i].join()
        loop = loop + 1

    return asset_info
