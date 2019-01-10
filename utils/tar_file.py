# -*- coding: utf8 -*- 
## http://zhujiangtao.com/?p=579

import os,tarfile
 
def make_tar(folder_to_tar,dst_folder,compression='bz2'):
    '''将folder_to_tar文件夹按照compression压缩格式，打包到dst_folder目录下
    默认使用bz2压缩，如果指定compression=None，则表示只打包不压缩'''
 
    #是否需要压缩
    if compression: #压缩
        dst_ext = '.'+compression #打包后文件的后缀名
    else:
        dst_ext=''
 
    #文件夹名称
    fold_name = os.path.basename(folder_to_tar)
 
    #打包的文件名称
    dst_name = '%s.tar%s'%(fold_name,dst_ext)#fold_name.tar.bz2
 
    #打包的文件全路径
    dst_path = os.path.join(dst_folder,dst_name) #dst_folder/fold_name.tar.bz2
 
    if compression:
        dst_cmp = ':'+compression #:bz2 :gz 等表示压缩格式
    else:
        dst_cmp = ''
 
    #打开一个tar文件
    tar = tarfile.TarFile.open(dst_path, 'w'+dst_cmp)
 
    #向tar文件中添加要打包的文件
    tar.add(folder_to_tar,fold_name)#打包该目录
 
    #关闭tar文件
    tar.close()
 
    #返回打包文件全路径
    return dst_path
