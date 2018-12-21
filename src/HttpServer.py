# -*- coding:utf-8 -*-
# 创建时间：2018-12-14 14:51:35
# 创建人：  Dekiven

import os
import SimpleHTTPServer
import SocketServer
import socket

def getLocalIp() :
    # 获取本机计算机名称
    hostname = socket.gethostname()
    # 获取本机ip
    ip = socket.gethostbyname(hostname)
    # print(ip)
    return ip

class HttpServer(object):
    """docstring for HttpServer"""
    def __init__(self):
        super(HttpServer, self).__init__()
        self.serverInstance = None
        

    def startServer(self, srcDir, port) :
        '''根据传入的文件夹路径和端口号创建http服务器'''
        self.stopServer()

        if os.path.isdir(srcDir) :
            curDir = os.getcwd()
            os.chdir(srcDir)
            Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

            httpd = SocketServer.TCPServer(('', port), Handler)

            self.serverInstance = httpd

            httpd.serve_forever()
            os.chdir(curDir)


    def stopServer(self) :
        if self.serverInstance is not None :
            # print('stopServer')
            self.serverInstance.shutdown()

def command() :
    import sys
    import getopt
    argv = sys.argv[1:]

    dirPath = ''
    port = 8000

    try:
        opts, args = getopt.getopt(argv,"d:p:",["dir=","port="])
    except getopt.GetoptError:
        print (u'获取参数错误')
        input(u'按任意键退出')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-d', '--dir') :
            dirPath = arg
        if opt in ('-p', '--port') :
            port = int(arg)
    # print(dirPath, port)
    if dirPath != '' and os.path.isdir(dirPath) and port > 0 :
        http = HttpServer()
        http.startServer(dirPath, port)
        print(u'参数不正确')

def __main() :
    # import threading
    # import time

    # http = HttpServer()

    # def threadFunc () :
    #     time.sleep(20)
    #     http.stopServer()
    # threading.Thread(target=threadFunc).start()

    # http.startServer(os.getcwd(), 8000)
    command()
    

if __name__ == '__main__' :
    __main()
