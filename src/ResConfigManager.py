# -*- coding:utf-8 -*- 
# Date: 2018-03-29 10:51:32
# Author: dekiven

import os
import json
import re

from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *

configFileName = 'base'
historyFileName = 'history.json'
crcConfExt = '.manifest'
cfgExt = '.bytes'

key_version_s = 'versions'
key_version = 'version'
key_files = 'files'
key_log = 'log'

class ResConfigManager(object) :
    '''ResConfigManager
    '''
    def __init__(self, path, version='0.0.0', outPath=None, testMode=False, packages={}) :
        super(ResConfigManager, self).__init__()
        self.path = None
        self.platform = None
        self.outPath = outPath
        self.testMode = testMode
        # self.packagesConf = packages
        self.packagePatterns = {}
        self.packageFiles = {}

        for k in tuple(packages.keys()) :
            self.packagePatterns[k] = re.compile('^'+packages.get(k)+'$')

        # 读取的配置
        # 可修改的配置
        self.history = {key_version_s:[], key_log:{}}
        self.conf = {key_version:version, key_files:{}}
        self.__initPath(path)
        self.loadConfig()
        self.pattenCRC = re.compile('^\s*CRC:\s*(\d+)\s*$')

    def __initPath(self, path) :
        self.platform = os.path.split(path)[-1]
        # print(self.platform)
        if not os.path.isabs(path) :
            path = pathJoin(getMainCwd(), path)
        path = path.replace('\\', '/')
        self.path = path
        if self.outPath is None :
            self.outPath = path
        if not os.path.isdir(path) :
            os.makedirs(path)
        fp = self.getHistoryPath()
        if not os.path.isfile(fp) :
            # pd = os.path.dirname(path)
            self.saveConfig(False, True)

    def getVersionDir(self, path=None) :
        return pathJoin(path or self.path, 'version')

    def getBasePath(self, path=None):
        return pathJoin(self.getVersionDir(path), configFileName+cfgExt)

    def getPkgCfgPath(self, pkg, path=None) :
        return pathJoin(self.getVersionDir(path), pkg+cfgExt)

    def getHistoryPath(self, path=None) :
        return pathJoin(self.getVersionDir(path), historyFileName)

    def setVersion(self, v) :
        self.conf[key_version] = v

    def loadConfig(self):
        # fp = self.getBasePath()
        # f = open(fp, 'rb')
        # jsonStr = f.read().encode('utf-8')
        # f.close()
        # self.conf = jsonLoads(jsonStr, encoding='utf-8')
        fp = self.getHistoryPath()
        f = open(fp, 'rb')
        jsonStr = bytes2utf8Str(f.read())
        f.close()
        self.history = jsonLoads(jsonStr, encoding='utf-8')

    def saveConfig(self, cur=True, history=False):
        if cur :
            self.saveCurVer()
        if history :
            self.saveHistroy()

    def saveHistroy(self) :
        fp = self.getHistoryPath()
        jsonStr = jsonDumps(self.history, indent=4, encoding='utf-8')
        d = os.path.dirname(fp)
        if not os.path.isdir(d) :
            os.makedirs(d)
        f = open(fp, 'w')
        f.write(jsonStr)
        f.close()

    def saveCurVer(self, conf=None, path=None):
        conf = conf or self.conf
        path = path or self.path
        pkgFiles = {}
        vdir = self.getVersionDir(path)
        if not os.path.isdir(vdir) :
            os.makedirs(vdir) 
        for fn in tuple(conf[key_files].keys()) :
            size = os.path.getsize(pathJoin(self.path, fn))
            pkg = self.getPkgName(fn)
            if pkg :
                fp = pkgFiles.get(pkg)
                if not fp :
                    fp = open(self.getPkgCfgPath(pkg, path=path), 'w')
                    fp.write('version|%s\n'%(conf[key_version]))
                    pkgFiles[pkg] = fp
                fp.write('%s|%s|%d\n'%(fn, self.conf[key_files][fn], size))
        for fp in tuple(pkgFiles.values()) :
            fp.close()

    def readResInfo(self, path) :
        f = open(path, 'rb')
        lines = f.readlines()
        f.close()

        l = bytes2utf8Str(lines[1])
        m = self.pattenCRC.match(l)
        if m :
            crc = m.group(1)
            p = self.getRelativePath(path).replace(crcConfExt, '')
            # print(p, crc)
            return (p, crc)

    def getCurResInfos(self, path=None) :
        data = []
        path = path or self.path
        for _dir, folders, files in os.walk(path) :
            for f in files :
                ext = os.path.splitext(f)[-1]
                if ext == crcConfExt :
                    p = pathJoin(_dir, f)
                    data.append(self.readResInfo(p))
        files = dict(data)
        self.conf[key_files] = files
        # print(files)
        return files.copy()


    def getRelativePath(self, p) :
        p = p.replace('\\', '/')
        path = self.path
        if os.path.isabs(p) and len(p) > len(path) :
            l = len(path)+1
        return p[l:]

    def getChangedInfo(self, diffFrom=None) :
        orifiles, version = self.getHistoryFromVer(diffFrom)
        files = self.getCurResInfos()

        for f, crc in files.items() :
            if crc == orifiles.get(f) :
                # 删除相同的文件
                del files[f]

        # 添加有修改的文件所对应的配置文件
        confs = []
        pkgs = self.getPkgNames(files)
        for pkg in pkgs :
            pkg = self.getRelativePath(self.getPkgCfgPath(pkg))
            confs.append(pkg)

        return files, confs


    def getHistoryFromVer(self, versionFrom=None) :
        orifiles = {}
        if versionFrom :
            versionFrom = [int(i) for i in versionFrom.split('.')]
        for v in self.history[key_version_s] :
            if versionFrom is None or [int(i) for i in v.split('.')] >= versionFrom :
                for f,crc in self.history[key_log][v].items() :
                    orifiles[f] = crc
            else :
                break
        version = self.history.get(key_version_s)
        if len(version) > 0 :
            version = version[-1]
        else :
            version = None
        return orifiles, version

    def addLog(self, version, files) :
        versions = self.history[key_version_s]
        # 测试模式不记录历史
        if not version in versions and len(list(files.keys())) > 0 and not self.testMode :
            self.history[key_version_s].append(version)
            self.history[key_log][version] = dict(files)
        self.saveConfig(False, True)

    def saveBaseResConfig(self, files, configPath) :
        hFiles, version = self.getHistoryFromVer()

        if version is None :
            ShowInfoDialog(u'请先点击资源更新按钮更新资源配置')
            return

        _files = {}
        for f in files :
            crc = hFiles.get(f)
            if crc is not None :
                _files[f] = crc
        
        conf = {}
        conf[key_version] = version + '.base'
        conf[key_files] = _files
        self.conf = conf
        self.saveCurVer(conf, configPath)
        return True

    def getPkgName(self, name) :
        name = os.path.split(name)[-1]
        for k in tuple(self.packagePatterns.keys()) :
            p = self.packagePatterns.get(k)
            if p :
                m = p.match(name)
                if m :
                    return k
        return configFileName

    def getPkgNames(self, files) :
        names = []
        for f in files :
            pkg = self.getPkgName(f)
            if pkg not in names :
                names.append(pkg)
        return names


def main() :
    version = '0.0.2'
    res = ResConfigManager('pc', version)
    # res.getCurResInfos()
    # res.saveConfig()
    # res.addLog('0.0.2', {'f1':'12345',})
    change = res.getChangedInfo()
    res.addLog(version, change)
    res.saveConfig()
    # TODO:zip and upload
    print('finished!')

if __name__ == '__main__':
    main()

