# -*- coding:utf-8 -*- 
# Date: 2018-04-03 09:08:22
# Author: dekiven

import os
import zipfile
import shutil

from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *
from TkToolsD.CommonWidgets import regEnterTip
from TkToolsD.VersionWidget import VersionWidget


tk, ttk = getTk()

try:
    from ProjConfigManager import ProjConfigManager
    from ResConfigManager import ResConfigManager
    from ResConfigManager import historyFileName
    from ConfigEditWindow import ConfigEditWindow
    from AsbPackageWindow import AsbPackageWindow
    from ResExplorer import ResExplorer
except Exception as e:
    from .ProjConfigManager import ProjConfigManager
    from .ResConfigManager import ResConfigManager
    from .ResConfigManager import historyFileName
    from .ConfigEditWindow import ConfigEditWindow
    from .AsbPackageWindow import AsbPackageWindow
    from .ResExplorer import ResExplorer
    

objPool = []
event_cbb = '<<ComboboxSelected>>'

STR_EXT = '.unity3d'

resPlatforms = ('and', 'ios', 'pc', 'mac',)
buildPlatAll = [ 
    # 'version', 
    'basicres'+STR_EXT, 
    'updateserver'+STR_EXT,
]
buildPlatAll = buildPlatAll + [p+STR_EXT for p in resPlatforms]

skipPatterns = (r'.*\.manifest', r'.*\.DS_Store', r'.*\.json', 'version', r'.*\.bytes')

key_curVersion = 'curVersion'
key_curPlatf = 'curPlatform'
key_projDir = 'dir'
key_backDir = 'dir_back'
key_serverDir = 'dir_server'
key_asbDir = 'dir_asb'
key_baseRes = 'baseRes'
key_servConf = 'servConf'
key_packageConf = 'asbPackages'

STR_F_SERV_CONFIG = 'servConf.bytes'

def relativeTo(path, root) :
    path = path.replace('\\', '/')
    root = root.replace('\\', '/')
    if path.find(root) == 0 :
        return path[len(root)+1:]

def copyFilesTo(src, target, files) :
    if os.path.isdir(src) :
        for f in files :
            rf = f.split(':')[0]
            if not os.path.isabs(f) :
                f = pathJoin(src, f)
            else :
                rf = relativeTo(f, src)
            if f.find(src) == 0 and os.path.isfile(f) :
                rp = pathJoin(target, rf)
                d = os.path.dirname(rp)
                if not os.path.isdir(d) :
                    os.makedirs(d)
                # print(f, rp)
                shutil.copyfile(f, rp)

class AppFrame(ttk.Frame):
    """docstring for AppFrame"""
    def __init__(self, *arg, **dArg):
        ttk.Frame.__init__(self, *arg, **dArg)
        self.confPath = None
        self.curProjName = None

        self.confProj = None
        self.confRes = None

        self.projCombo = None
        self.projDirWid = None
        self.backDirWid = None
        self.platCombo = None
        self.newVerWid = None
        self.baseResWid = None   #配置基础资源暂时先不考虑实现
        self.newProEntry = None
        self.fileExplorer = None
        self.packageFiles = {}

        self.fileChanges = False
        self.setFiles([])

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        counter = getCounter()

        # 项目选择
        projCombo = self.__getComboboxWidget(self, u'项目选择', 'id_proj_cbb')
        projCombo.grid(column=0, row=counter(), padx=5, pady=5)
        self.projCombo = projCombo

        # 项目路径
        dirCallback = self.__onProjDirChange
        projDirWid = GetDirWidget(self, u'项目路径', u'u3d项目路径,Assets父目录。', callback=dirCallback)
        projDirWid.grid(column=0, row=counter(), padx=5, pady=5, sticky='we')
        self.projDirWid = projDirWid

        # 项目导出 asb 路径
        dirCallback = self.__onProjAsbDirChange
        projAsbDirWid = GetDirWidget(self, u'Asb路径', u'项目导出 asb 路径,默认是：项目路径/AssetBundles', callback=dirCallback)
        projAsbDirWid.grid(column=0, row=counter(), padx=5, pady=5, sticky='we')
        self.projAsbDirWid = projAsbDirWid

        # 资源历史版本备份路径
        dirCallback = self.__onBackDirChange
        backDirWid = GetDirWidget(self, u'备份路径', u'资源历史版本备份路径。', callback=dirCallback)
        backDirWid.grid(column=0, row=counter(), padx=5, pady=5, sticky='we')
        self.backDirWid = backDirWid

        # 资源更新服务器路径
        dirCallback = self.__onServerDirChange
        serverDirWid = GetDirWidget(self, u'服务器路径', u'资源更新服务器路径', callback=dirCallback)
        serverDirWid.grid(column=0, row=counter(), padx=5, pady=5, sticky='we')
        self.serverDirWid = serverDirWid

        # 项目版本管理
        newVerWid = VersionWidget(self)
        newVerWid.setVersionLen(4)
        newVerWid.setSubMaxVerLen(2)
        newVerWid.setCallback(self.__onVersionChange)
        newVerWid.grid(column=0, row=counter(), padx=5, pady=5)
        self.newVerWid = newVerWid


        # ==========================平台配置 begin=============================
        lf = ttk.LabelFrame(self, text=u'平台配置')
        lf.columnconfigure(0, weight=1)
        lf.grid(column=0, row=counter(), padx=5, pady=5, sticky='nswe')

        btn = ttk.Button(lf, text=u'服务器配置', command=self.__onClickConfig)
        btn.grid(column=1, row=0)

        btn = ttk.Button(lf, text=u'asb分包配置', command=self.__onClickPkgConfig)
        btn.grid(column=0, row=0)

        # ==========================平台配置 end===============================

        # 资源提交地址
        # 提交资源更新（Button）
        # --------------------------资源管理 begin------------------------------
        lf = ttk.LabelFrame(self, text=u'资源管理')
        lf.grid(column=0, row=counter(), padx=5, pady=5, sticky='nswe')
        btns = []
        c2 = getCounter()

        # 资源平台选择
        platCombo = self.__getComboboxWidget(lf, u'打包平台', 'id_plat_cbb', resPlatforms)
        platCombo.grid(column=c2(), row=0, padx=5, pady=5)
        self.platCombo = platCombo

        btn = ttk.Button(lf, text=u'更新打包资源', command=self.__onBaseResBtn)
        btn.grid(column=c2(), row=0, padx=5, pady=5)
        btns.append(btn)
        tip = regEnterTip(btn, text=u'将选择平台打包资源拷贝到打包路径.\n拷贝前先做资源更新。')


        btn = ttk.Button(lf, text=u'资源更新', command=self.__onUpdateBtn)
        btn.grid(column=c2(), row=0, padx=5, pady=5)
        btns.append(btn)
        tip = regEnterTip(btn, text=u'更新所有平台资源版本信息，\n并备份到备份路径下。')

        for i in range(len(btns)) :
            lf.columnconfigure(i, weight=1)
        
        # ==========================资源管理 end===============================

        lf = ttk.LabelFrame(self, text=u'新增项目')
        lf.columnconfigure(0, weight=1)
        lf.grid(column=0, row=counter(), padx=5, pady=5)

        newProEntry = ttk.Entry(lf)
        self.newProEntry = newProEntry
        newProEntry.grid(column=0, row=0)

        btn = ttk.Button(lf, text=u'新增项目', command=self.__onNewProj)
        btn.grid(column=1, row=0)

        btn = ttk.Button(lf, text=u'保存配置', command=self.saveCurProj)
        btn.grid(column=2, row=0)

        mfc = ResExplorer(self)
        mfcRow = counter()
        self.rowconfigure(mfcRow, weight=1)
        mfc.grid(column=1, row=0, rowspan=mfcRow+1, padx=5, pady=5, sticky='nswe')
        mfc.setChoosenCallback(self.__onFileChoosen)
        self.fileExplorer = mfc

        ttk.Frame(self).grid(column=0, row=mfcRow)

    def __getComboboxWidget(self, pWidget, head, widid, values=(), current=0) :
        frame = ttk.Frame(pWidget)
        frame.columnconfigure(1, weight=1)

        lb = ttk.Label(frame, text=head)
        lb.grid(column=0, row=0, padx=20, pady=5)

        sv = tk.StringVar()  
        cbb = ttk.Combobox(frame, textvariable=sv)  
        cbb['values'] = values
        if len(values) > current :
            cbb.current(current)  #设置初始显示值，值为元组['values']的下标  
        cbb.grid(column=1, row=0, sticky='nswe', padx=20, pady=5)
        cbb.config(state='readonly')  #设为只读模式 
        cbb.widid = widid
        cbb.bind(event_cbb, self.__getEventCallFunc(cbb, event_cbb))

        frame.sv = sv
        frame.current = cbb.current
        def setValues(v) :
            cbb['values'] = v
        frame.setValues = setValues
        frame.get = cbb.get
        frame.set = sv.set

        # 必须将sv对象保存，以免被释放，类似img  →_→
        objPool.append(sv)
        # objPool.append(cbb)
        return frame

    def __getEventCallFunc(self, sender, evenStr) :
        params = (sender, evenStr)
        def func(*args):
            self.__onEvent(params[0], params[1], *args)
        return func

    def __onEvent(self, sender, evenStr, *args) :
        name = sender.widid
        if evenStr == event_cbb :
            if name == 'id_proj_cbb' :
                # 项目选择
                self.selectAProj(sender.get())
            elif name == 'id_plat_cbb' :
                # 打包平台选择
                self.__onChangePlat(sender.get())
                self.saveCurProj()
                self.loadConfigs()

    def __onProjDirChange(self, path) :
        rst = self.confProj.changeProjConfig(self.curProjName, key_projDir, path)
        # self.saveConfigs()

    def __onProjAsbDirChange(self, path) :
        rst = self.confProj.changeProjConfig(self.curProjName, key_asbDir, path)

    def __onBackDirChange(self, path) :
        rst = self.confProj.changeProjConfig(self.curProjName, key_backDir, path)

    def __onServerDirChange(self, path) :
        rst = self.confProj.changeProjConfig(self.curProjName, key_serverDir, path)
        self.saveConfigs()

    def __onVersionChange(self, v) :
        self.confProj.changeProjConfig(self.curProjName, key_curVersion, v)
        # self.saveConfigs()

    def __onUpdateBtn(self) :
        if ShowAskDialog(u'更新资源版本信息之前，请确认\n当前平台的资源已经是最新！\n=====点确定继续。=====') :
            version = self.getProjConfig(key_curVersion)
            # plat = self.getProjConfig(key_curPlatf)
            pPath = self.getProjConfig(key_projDir)
            bPath = self.getProjConfig(key_backDir)
            projName = self.curProjName
            if pPath == '' or bPath == '':
                ShowInfoDialog(u'项目路径和备份路径不能为空！\n注意：不能包含中文！！！')
                return

            # if plat == 'all' :
            #   plat = buildPlatAll
            # else :
            #   plat = (plat,)
            # print('update "%s" to version:"%s" ...'%(projName, version))
            # 暂时不检测版本号更新
            if self.newVerWid.hasVersionChanged() or True:
                # TODO: 生成更新日志和当前文件配置表，复制更改的文件备份并上传
                # for _plat in plat :
                _plat = self.platCombo.get()
                rPath = self.getBundlePath(_plat)
                sPath = self.getBServerPath(_plat)
                res = ResConfigManager(rPath, version, packages=self.__getCurPackageConf())
                # res.getCurResInfos()
                # res.saveConfig()
                # res.addLog('0.0.2', {'f1':'12345',})
                change, pkgs = res.getChangedInfo()
                if len(list(change.keys())) > 0 :
                    # 添加历史信息
                    res.addLog(version, change)
                    # 保存 bytes 文件
                    res.saveConfig()
                    change = list(change.keys())
                    change += pkgs
                    # 增量备份并 zip 
                    self.backRes(
                        rPath, 
                        pathJoin(bPath, '%s/%s'%(projName, _plat)), 
                        _plat, 
                        version, 
                        change, 
                        res.getHistoryPath()
                    )
                    # 增量将修改文件复制到本地资源服路径
                    self.updateServer(rPath, sPath, version, change)
                    ShowInfoDialog(u'更新%s版本%s信息完成！'%(version, _plat))
                else :
                    ShowInfoDialog('没有资源更新\n请检查资源或者重新build Assetbundle')

            else :
                ShowInfoDialog(u'版本号没有变更！')
            self.saveCurProj()

    def __onBaseResBtn(self) :
        # ShowInfoDialog(u'待实现！')
        version = self.getProjConfig(key_curVersion)
        plat = self.getProjConfig(key_curPlatf)
        pPath = self.getProjConfig(key_projDir)
        self.saveBaseResConf()

        sPath = self.getStreamingPath()
        if os.path.isdir(sPath) :
            removeTree(sPath)
        sPath = pathJoin(sPath, plat)
        aPath = self.getBundlePath(plat)
        copyFilesTo(aPath, sPath, self.getFiles())
        res = ResConfigManager(aPath, packages=self.__getCurPackageConf())
        if res.saveBaseResConfig(self.getFiles(), sPath) :
            ShowInfoDialog(u'平台:"%s"\n版本:"%s"\n资源拷贝完成,可以使用U3D Editor打包。'%(plat, version+'.base'))

    def __onClickConfig(self):
        ce = ConfigEditWindow(self)
        conf = self.getProjConfig(key_servConf)
        if conf is None :
            self.changeProjConfig(key_servConf, {})
        ce.setCallback(self.__onServConfChanged)
        ce.setData( conf or {}, resPlatforms)
        centerToplevel(ce)
        root = getToplevel(self)
        root.wait_window(ce)

    def __onServConfChanged(self, key, data) :
        conf = self.getProjConfig(key_servConf) or {}
        conf[key] = data
        self.changeProjConfig(key_servConf, conf)
        self.__saveServConfig(key, data)
        self.saveCurProj()

    def __saveServConfig(self, key, data) :
        if key in resPlatforms :
            asbDir = self.getProjConfig(key_asbDir)
            pPath = pathJoin(asbDir, key)
            if not os.path.isdir(pPath) :
                os.makedirs(pPath)
            f = open(pathJoin(pPath, STR_F_SERV_CONFIG), 'w')
            for k  in tuple(data.keys()) :
                f.write('%s|%s\n'%(k, str(data.get(k)[1])))
            # TODO:
            f.close()

    def __saveAllServConf(self) :
        for key in resPlatforms :
            conf = self.getProjConfig(key_servConf) or {}
            data = conf.get(key) or {}
            self.__saveServConfig(key, data)

    def __onClickPkgConfig(self):
        ce = AsbPackageWindow(self)
        conf = self.getProjConfig(key_packageConf)
        if conf is None :
            conf = {}
            self.changeProjConfig(key_packageConf, conf)
        ce.setCallback(self.__onPkgConfChanged)
        ce.setData( conf )
        centerToplevel(ce)
        root = getToplevel(self)
        root.wait_window(ce)

    def __onPkgConfChanged(self, data) :
        # conf = self.getProjConfig(key_packageConf) or {}
        # conf[key] = data
        self.changeProjConfig(key_packageConf, data)
        self.saveCurProj()
        self.freshUI()


    def getBundlePath(self, platform) :
        # or '' 旧版本适配
        rPath = self.getProjConfig(key_asbDir) or ''
        if rPath == '' :
            pPath = self.getProjConfig(key_projDir)
            if pPath is None :
                return None
            rPath = pathJoin(pPath, 'AssetBundles')
            self.projAsbDirWid.setValue(rPath)
            self.confProj.changeProjConfig(self.curProjName, key_asbDir, rPath)
        rPath = pathJoin(rPath, platform)
        return rPath

    def getBServerPath(self, platform) :
        pPath = self.getProjConfig(key_serverDir)
        if pPath is None :
            return None
        rPath = pathJoin(pPath, platform)
        return rPath

    def getStreamingPath(self) :
        pPath = self.getProjConfig(key_projDir)
        if pPath is None :
            return None
        sPath = pathJoin(pPath, 'Assets/StreamingAssets')
        return sPath

    def getProjConfig(self, key) :
        if self.curProjName != '' :
            return self.confProj.getProjConfig(self.curProjName, key)

    def changeProjConfig(self, key, value) :
        if self.curProjName != '' :
            self.confProj.changeProjConfig(self.curProjName, key, value)

    def __onNewProj(self) :
        pn = self.newProEntry.get()
        if pn != '' :
            self.confProj.addProj(pn, {
                "curPlatform": "pc", 
                "curVersion": "0.0.0.0", 
                "baseRes": [], 
                "dir": "", 
                "dir_back": "",
                "dir_asb": ""
            })
            # self.saveConfigs()
            self.setFiles([])
            self.fileExplorer.clearItems()
            self.selectAProj(pn)
            self.saveCurProj()
            self.loadConfigs()

    def __onChangePlat(self, plat) :
        self.confProj.changeProjConfig(self.curProjName, key_curPlatf, plat)
        # self.saveConfigs()

    def __onFileChoosen(self, files) :
        root = self.getProjConfig(key_projDir)
        if os.path.isdir(root) :
            plat = self.getProjConfig(key_curPlatf) or 'pc'
            pcRes = self.getBundlePath(plat)
            self.fileChanges = True
            self.setFiles([relativeTo(f, pcRes) for f in files])
            self.fileExplorer.setChoosenFiles(self.getFiles())

    def __getCurPackageConf(self) :
        '''获取当前项目的 asb 资源包配置
        '''
        data = self.getProjConfig(key_packageConf) or {}
        conf = {}
        for k in tuple(data.keys()) :
            d = data.get(k)
            conf[k] = d[1]  
        return conf


    def loadConfigs(self, confPath=None) :
        confPath = confPath or self.confPath
        self.confPath = confPath
        self.confProj = ProjConfigManager(confPath)
        self.projCombo.setValues(self.confProj.getProjNames())

        curProjName = self.confProj.getCurProjName()
        if curProjName != '' :
            self.selectAProj(curProjName)

    def saveConfigs(self) :
        # if proj :
        self.confProj.saveConfig()

        # if res and self.confRes :
        #   self.confRes.saveConfig()

    def saveCurProj(self) :
        self.changeProjConfig(key_projDir, self.projDirWid.et.get())
        self.changeProjConfig(key_backDir, self.backDirWid.et.get())
        self.changeProjConfig(key_curPlatf, self.platCombo.get())
        self.changeProjConfig(key_curVersion, self.newVerWid.getVersion())
        self.changeProjConfig(key_serverDir, self.serverDirWid.et.get())
        # self.changeProjConfig(self.curProjName, key_baseRes, self.fileExplorer.getChoosenFiles())
        self.saveBaseResConf()
        self.saveConfigs()

    def saveBaseResConf(self) :
        if self.fileChanges :
            if ShowAskDialog(u'是否改变包内资源配置？') :
                self.changeProjConfig(key_baseRes, self.getFiles())
                self.fileChanges = False;
            else :
                files = self.getProjConfig(key_baseRes) or []
                self.fileExplorer.setChoosenFiles(self.getFiles(files))
                self.setFiles(files)
        self.saveConfigs()

    def selectAProj(self, name) :
        self.curProjName = name
        conf = self.confProj.getProjConfig(name)
        if conf :
            self.projCombo.set(name)
            self.confProj.setCurProj(name)
            self.projDirWid.setValue(conf.get(key_projDir) or '')
            self.backDirWid.setValue(conf.get(key_backDir) or '')
            self.serverDirWid.setValue(conf.get(key_serverDir) or '')
            self.projAsbDirWid.setValue(conf.get(key_asbDir) or '')
            plat = conf.get(key_curPlatf) or 'pc'
            self.platCombo.set(plat)
            version = conf.get(key_curVersion) or '0.0.0.0'
            self.newVerWid.setCurVersion( version)
            self.newVerWid.setVertion( version )
            pcRes = self.getBundlePath(plat)
            files = conf.get(key_baseRes) or []
            self.fileExplorer.clearItems()
            
            self.packageFiles = self.fileExplorer.setPath(
                pcRes, 
                skipPatterns,
                self.getFiles(files), 
                self.__getCurPackageConf()
            )
            # self.fileExplorer.setPath(pcRes, ('.manifest', ""), files)
            self.setFiles(files)
            self.fileChanges = False
            # self.saveConfigs()  

            # 生成服务器配置文件
            self.__saveAllServConf()    

    def backRes(self, path, outPath, plat, version, files, histroyPath) :
        if len(files) == 0 :
            # print(u'没有资源变动，不打包备份。')
            return
        # print(files)
        zipName = '%s_v_%s.zip'%(plat, version)
        if not os.path.isdir(path) :
            # print(u'资源文件夹"%s"不存在！！！'%(path))
            return

        if not os.path.isdir(outPath) :
            os.makedirs(outPath)

        zf = zipfile.ZipFile(pathJoin(outPath, zipName), 'w')
        files = list(files)
        # 添加服务器配置文件
        files.append(STR_F_SERV_CONFIG)

        for f in files :
            p = pathJoin(path, f) 
            if os.path.isfile(p) :
                zf.write(p, pathJoin(plat, f))
        zf.close()
        shutil.copyfile(histroyPath, pathJoin(outPath, historyFileName))

    def updateServer(self, path, outPath, version, files) :
        if len(files) == 0 :
            # print(u'没有资源变动，不打包备份。')
            return
        # zipName = 'v_%s.zip'%(version)
        if not os.path.isdir(path) :
            # print(u'资源文件夹"%s"不存在！！！'%(path))
            return

        if not os.path.isdir(outPath) :
            os.makedirs(outPath)
        files = list(files)
        # 添加服务器配置文件
        files.append(STR_F_SERV_CONFIG)


        for f in files :
            tp = pathJoin(outPath, f)
            tpdir = os.path.dirname(tp)
            if not os.path.exists(tpdir) :
                os.makedirs(tpdir)
            try:
                shutil.copyfile(pathJoin(path, f), pathJoin(outPath, f))
            except Exception as e:
                ShowInfoDialog(str(e))    

    def setFiles(self, files) :
        # buildPlatAll 定义的渠道名是特殊的资源，每个渠道不同，但所有渠道都需要
        self.choosenFiles = list(set(files) | set(buildPlatAll))

    def getFiles(self, files=None) :
        # buildPlatAll 定义的渠道名是特殊的资源，每个渠道不同，但所有渠道都需要
        files = files or self.choosenFiles
        return list(set(files) | set(buildPlatAll))

    def clearCurProj(self) :
        return
        # TODO:清空历史资源等
        self.newVerWid.setVertion('0.0.0.1')
        self.newVerWid.setCurVersion('0.0.0.0')
        self.saveCurProj()
        self.selectAProj(self.projCombo.get())

    def freshUI(self):
        self.selectAProj(self.curProjName)

