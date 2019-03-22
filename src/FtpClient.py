# -*- coding:utf-8 -*-
# 创建时间：2018-12-14 17:03:43
# 创建人：  Dekiven

import os
from DKVTools.Funcs import *
from ftplib import FTP
import threading
import time

class FtpClient(FTP) :
    '''FtpClient
    '''

    def __init__(self, *args, **dArgs) :
        FTP.__init__(self, *args, **dArgs)
        self.host = None
        self.port = None
        self.userName = None
        self.password = None


    def connect(self, host='', port=0, userName='anonymous', password='anonymous@', timeout=None) :
        '''Connect to the given host and port. The default port number is 21, as specified by the FTP protocol specification. It is rarely needed to specify a different port number. This function should be called only once for each instance; it should not be called at all if a host was given when the instance was created. All other methods can only be used after a connection has been made. The optional timeout parameter specifies a timeout in seconds for the connection attempt. If no timeout is passed, the global default timeout setting will be used. source_address is a 2-tuple (host, port) for the socket to bind to as its source address before connecting.
Changed in version 3.3: source_address parameter was added.
        '''
        self.host = host
        self.port = port
        self.userName = userName
        self.password = password

        FTP.connect(self, host, port) #连接
        FTP.login(self, userName, password) #登录，如果匿名登录则用空串代替即可

    def setDebugLevel(self, level):
        # 级别2显示详细信息， 级别0关闭调试模式
        FTP.set_debuglevel(self, level) 

    def tryMkd(self, dirPath, relative2Root=False):
        curDir = self.pwd()[1:]
        if relative2Root :
            self.cwd('../'*len(curDir.split('/')))

        dirs = dirPath.split('/')
        for d in dirs :
            try:
                self.cwd(d)
            except Exception as e:
                try:
                    self.mkd(d)
                    self.cwd(d)
                except Exception as e:
                    print('makedir failed, please check your permission!')
                    # 还原 ftp 工作目录
                    if relative2Root :
                        self.cwd(curDir)
                    return
        if len(dirs) > 0 :
            self.cwd('../'*len(dirs))

        # 还原 ftp 工作目录
        if relative2Root :
            self.cwd(curDir)

    def ls(self, _dir='.') :
        '''返回指定路径的内容，默认为当前工作路径
返回内容格式:[[filename, permission, fileSize, modifyTime],... ]
fileSize 仅对文件有效，文件夹数据不正确
        '''
        import re

        p = re.compile(r'(\S+)\s+(\d+)\s+(.+)\s+(\d+)\s+(\S{3}\s+\d{2}\s+\d{2,}:?\d{2}?)\s+(\S.*)')

        lines = []
        self.dir(_dir, lines.append)

        content = []

        for l in lines :
            m = p.match(l)
            if m :
                content.append([m.group(6), m.group(1), m.group(4), m.group(5)])
            else :
                print('ls can not macth line: "%s"'%l)

        return content

    def walk(self, _dir='.') :
        ret = []
        fds = []
        fs = []
        for l in self.ls(_dir) :
            if l[1].startswith('d') :
                # 如果是文件夹
                d = l[0]
                fds.append(d)
                ret += self.walk(pathJoin(_dir, d))
            else :
                fs.append(l[0])
        ret.insert(0, [_dir, fds, fs])

        return ret

    #文件上传
    def upload(self, filePath, fname, blocksize=8192 , callback=None, mdk=True, ftp=None):
        ftp = ftp or self
        fname = formatPath(fname)
        if fname.startswith('/') :
            fname = fname[1:]

        if os.path.isfile(filePath) :
            size = os.path.getsize(filePath)
            count = [0,]
            def __c(content) :
                count[0] += len(content)
                if callback :
                    callback(min(1, count[0]/float(size)))
            fd = open(filePath, 'rb')
            try:
                d = os.path.split(fname)[0]
                if d != '' and mdk:
                    self.tryMkd(d)
                #以二进制的形式上传
                ftp.storbinary("STOR %s" % fname, fd, blocksize=blocksize, callback=__c)
                if size == 0 :
                    callback(1)
            except Exception as e:
                if callback :
                    callback(-1, e)
            finally:
                fd.close()
        # print("upload finished")

    #文件下载
    def download(self, fname, saveDir, callback=None, ftp=None) :
        ftp = ftp or self
        pdir = os.path.dirname(saveDir)
        if not os.path.isdir(pdir) :
            os.makedirs(pdir)
        fd = open(saveDir, 'wb')
        size = ftp.size(fname)
        count = [0,]
        def __c(content) :
            count[0] += len(content)
            fd.write(content)
            if callback :
                    callback(min(1, count[0]/float(size)))
        try:
            if size > 0 :
                #以二进制形式下载，注意第二个参数是fd.write，上传时是fd
                ftp.retrbinary("RETR %s" % fname, callback=__c)
        except Exception as e:
            if callback :
                callback(-1, e)
        finally:
            fd.close()  
        if size == 0 :
            callback(1)   

    def uploadDir(self, dirPath, ftpPath, callback=None, threadNum=4, isDaemon=False) :
        if not os.path.isdir(dirPath) :
            print('can not upload dir, dirPath :"%s" do not exist!!'%dirPath)
            return
        filePaths = []
        fNames = []
        newDirs = []

        for _dir, fds, fs in os.walk(dirPath) :
            relaPath = getRelativePath(_dir, dirPath)[0]
            if len(relaPath) > 0 :
                relaPath = pathJoin(ftpPath, relaPath)
            else :
                relaPath = ftpPath
            if relaPath not in newDirs :
                # TODO:优化减少不必要的 dir
                newDirs.append(relaPath)
            for f in fs :
                if f != '.DS_Store' :
                    filePaths.append(pathJoin(_dir, f))
                    fNames.append(pathJoin(relaPath, f))

        self.uploadFiles(filePaths, fNames, callback=callback, threadNum=threadNum)


    def uploadFiles(self, filePaths, fNames, callback=None, threadNum=4, newDirs=None, isDaemon=False) :
        if newDirs is None :
            newDirs = []
            for f in fNames :
                d = os.path.split(f)[0]
                if d != '' and d not in newDirs :
                    # TODO:优化减少不必要的 dir
                    newDirs.append(d)

        for d in newDirs :
            self.tryMkd(d)

        self.__startThread(filePaths, fNames, True, callback=callback, threadNum=threadNum, isDaemon=isDaemon)

    def downloadDir(self, ftpPath, savePath, callback=None, threadNum=4, isDaemon=False) :
        ftpPaths = []
        savePaths = []
        savePath = savePath.rstrip('/')
        for _dir, fds, fs in self.walk(ftpPath) :
            for f in fs :
                p = pathJoin(_dir, f)
                ftpPaths.append(p)
                savePaths.append(p.replace(ftpPath, savePath))

        self.downloadFiles(ftpPaths, savePaths, callback=callback, threadNum=threadNum)

    def downloadFiles(self, ftpPaths, savePaths, callback=None, threadNum=4, isDaemon=False) :
        self.__startThread(ftpPaths, savePaths, False, callback=callback, threadNum=threadNum, isDaemon=isDaemon)

    def __getMove2Next(self, arg1, arg2) :

        lock = threading.Lock()
        data = [-1, arg1, arg2]

        def move2Next() :
            lock.acquire()
            data[0] += 1
            a1, a2 = None, None
            idx = data[0]
            if idx < len(data[1]) and len(data[1]) == len(data[2]) :
                a1, a2 = data[1][idx], data[2][idx]
            lock.release()
            return a1, a2

        return move2Next

    def __startThread(self, arg1, arg2, isUp, callback=None, threadNum=4, isDaemon=False) :
        move2Next = self.__getMove2Next(arg1, arg2)

        def downloadThread() :
            data = [None] * 3
            ftp = FTP()
            ftp.connect(self.host, self.port)
            ftp.login(self.userName, self.password)

            def call(progress, exception=None) :
                if callback :
                    callback(data[1], progress, exception)
                data[2] = progress

                if cmp(abs(progress), 1) == 0 :
                    path, name = move2Next()
                    data[0] = path
                    data[1] = name
                    data[2] = None
    
            path, name = move2Next()
            data[0] = path
            data[1] = name
            data[2] = None
            
            while True :
                path, name = data[0], data[1]
                if data[0] is not None and data[2] is None :
                    data[2] = 0
                    if isUp :
                        self.upload(path, name, mdk=False, callback=call, ftp=ftp)
                    else :
                        self.download(path, name, callback=call, ftp=ftp)
                elif data[0] is None :
                    break
                time.sleep(1)
            ftp.quit()

        for i in range(threadNum) :
            t = threading.Thread(target=downloadThread)
            t.setDaemon(isDaemon)
            t.start()
        # downloadThread()

def __main() :
    # print('Module named:'+str(FtpClient))
    help(FTP)
if __name__ == '__main__' :
    __main()
