# -*- coding:utf-8 -*-
# 创建时间：2018-12-14 17:03:43
# 创建人：  Dekiven

import os
from ftplib import FTP

class FtpClient(object) :
    '''FtpClient
    '''
    def __init__(self, *args, **dArgs) :
        super(FtpClient, self).__init__(*args, **dArgs)

    def connect(self, ip, port, userName='', password='') :
        ftp=FTP()

        ftp.connect(ip, port) #连接
        ftp.login(userName, password) #登录，如果匿名登录则用空串代替即可

        self.ftp = ftp

    def setDebugLevel(self, level):
        # 级别2，显示详细信息
        ftp.set_debuglevel(level) 

    #文件上传
    def upload(self, filePath, fname):
        if os.path.isfile(filePath) :
            fd = open(filePath, 'rb')
            #以二进制的形式上传
            ftp.storbinary("STOR %s" % fname, fd)
            fd.close()
        # print("upload finished")
        
    #文件下载
    def download(self, fname, saveDir):
        pdir = os.path.dirname(saveDir)
        if not os.path.isdir() :
            os.makedirs(pdir)
        fd = open(saveDir, 'wb')
        #以二进制形式下载，注意第二个参数是fd.write，上传时是fd
        ftp.retrbinary("RETR %s" % fname, fd.write)
        fd.close()
        # print("download finished")


def __main() :
    # print('Module named:'+str(FtpClient))
    help(FTP)

if __name__ == '__main__' :
    __main()
