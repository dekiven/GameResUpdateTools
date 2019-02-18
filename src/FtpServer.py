# -*- coding:utf-8 -*-
# 创建时间：2018-12-14 15:52:04
# 创建人：  Dekiven

import os

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
'''
Read permissions: 
“e” = change directory (CWD, CDUP commands) 
“l” = list files (LIST, NLST, STAT, MLSD, MLST, SIZE commands) 
“r” = retrieve file from the server (RETR command) 
Write permissions: 
“a” = append data to an existing file (APPE command) 
“d” = delete file or directory (DELE, RMD commands) 
“f” = rename file or directory (RNFR, RNTO commands) 
“m” = create directory (MKD command) 
“w” = store a file to the server (STOR, STOU commands) 
“M” = change mode/permission (SITE CHMOD command) New in 0.7.0
'''


class FtpServer(object) :
    '''FtpServer
    '''
    def __init__(self, *args, **dArgs) :
        super(FtpServer, self).__init__(*args, **dArgs)
        self.server = None

    def initServer(self, srcDir, **dArgs):
        '''
        banner                  欢迎词，不填默认 pyftpdlib based ftpd ready.
        ip                      ip，不填默认‘0.0.0.0’
        port                    端口号，不填默认21
        max_cons                最大连接数，不填默认256
        max_cons_per_ip         每个ip最大连接数         
        masquerade_address      伪装IP,也就是被动模式，用于NAT（网址转换）之后，比喻服务器在防火墙、路由器后面的情况，默认不开启
        passive_ports           被动传输时指定端口，参数是一个整数列表,默认关闭；当伪装ip和端口同时存在时开启被动模式，前提是支持NAT
        '''
        self.stop()

        def getArg(key, default) :
            return dArgs.get(key) or default

        # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        self.initUsers(authorizer, srcDir)

        # Instantiate FTP handler class
        handler = FTPHandler
        handler.authorizer = authorizer

        # Define a customized banner (string returned when client connects)
        handler.banner = getArg('banner', "pyftpdlib based ftpd ready.")

        # Specify a masquerade address and the range of ports to use for
        # passive connections.  Decomment in case you're behind a NAT.

        ma = getArg('masquerade_address', None)
        pp = getArg('passive_ports', None)
        if ma and pp :
            # TODO:这里没有检测NAT是否支持
            handler.masquerade_address = ma
            handler.passive_ports = pp

        # Instantiate FTP server class and listen on 0.0.0.0:21
        address = (getArg('ip', ''), getArg('port', 2121))
        server = FTPServer(address, handler)

        # set a limit for connections
        server.max_cons = getArg('max_cons', 256)
        server.max_cons_per_ip = getArg('max_cons_per_ip', 5)

        self.server = server

    def initUsers(self, authorizer, srcDir) :
        if os.path.isdir(srcDir) and authorizer is not None :
            # Define a new user having full r/w permissions and a read-only
            # anonymous user
            # add_user(username,password,homedir,perm=”elr”,msg_login=”Login successful.”, msg_quit=”Goodbye.”)
            authorizer.add_user('user', '12345', '.', perm='elradfmwM')
            authorizer.add_anonymous(srcDir)
            return True
        return False

    def start(self) :
        # self.stop(False)
        if self.server is not None :
            # start ftp server
            self.server.serve_forever()

    def stop(self, claer=True) :
        if self.server is not None :
            self.server.close_all()
            if claer :
                self.server = None

def __main() :
    # print('Module named:'+str(FtpServer))
    # print(type(FTPServer.close))
    ser = FtpServer()
    # mac In unix (Linux, Mac OS X, BSD etc) systems, ports less than 1024 can not be bound to by normal users, only the root user can bind to those ports.
    ser.initServer('C:/Users/Dekiven/Desktop/fp', ip='192.168.199.137', port=21)
    ser.start()


if __name__ == '__main__' :
    __main()
