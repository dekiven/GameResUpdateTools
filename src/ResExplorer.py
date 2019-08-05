# -*- coding:utf-8 -*- 
# Date: 2019-06-17 11:25:38
# Author: dekiven

import os
import time

from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *
from TkToolsD.ImgView import *
from TkToolsD.ScrollFrame import *
import re

tk, ttk = getTk()

if isPython3() :
    from tkinter.font import Font
else :
    from tkFont import Font 

THIS_DIR = os.path.abspath(os.path.dirname(__file__))


class ResExplorer(ScrollFrame) :
    '''GameFramework 资源浏览器，可以区分资源包
    '''
    def __init__(self, *args, **dArgs) :
        ScrollFrame.__init__(self, *args, **dArgs) 

        self.selectedMulti = ()
        self.selectedAll = False
        self.tv = None

        self.rootPath = ''

        self.rowHeight = 20
        self.skipPatterns = ()
        self.packagePatterns = []
        self.packageFiles = {}
        self.choosenFiles = ()
        self.timeStamp = time.time()
        self.callback = None
        self.lastOpenClose = None

        self.tagNames = ('f_normal', 'f_checked', 'd_normal', 'd_part', 'd_checked', )
        self.__imgs = {}
        self.items = {
            # name : [path, isDir, status]
        }
        self.files = {}
        self.dirs = {}

        self.style = ttk.Style(self)

        tv = ttk.Treeview(self)
        self.setCenter(tv)
        self.tv = tv

        handleToplevelQuit(self, self.__onDestroy)
        self.setRowHeight(self.rowHeight)

        self.__registEvents()

        controlFuncs = {
            'a':self.selectAll,
        }
        self.controlFuncs = controlFuncs
        self.rightClickFunc = None

    def __registEvents(self):
        self.tv.bind('<<TreeviewSelect>>', self.__onSelected)
        self.tv.bind('<<TreeviewOpen>>', self.__onOpen)
        self.tv.bind('<<TreeviewClose>>', self.__onClose)
        self.tv.bind('<Control-Any-KeyRelease>', self.__onControlKey)
        # 鼠标中键和右键弹出菜单，mac双击触控板是button2（中键）
        self.tv.bind('<Button-2>', self.__onRightClick)
        self.tv.bind('<Button-3>', self.__onRightClick)
        # self.tv.bind('<Control-Any-KeyPress>', self.__onControlKey)
        # 注册控件大小改变事件监听
        self.tv.bind('<Configure>', self.updateContentSize)

    def __releaseIcons(self) :
        for k in tuple(self.__imgs.keys()) :            
            self.__releaseIcon(k)

    def __releaseIcon(self, key) :
        i = self.__imgs.get(key)
        if i is not None:
            i.release()
            del i

    def __onSelected(self, event):
        item = self.tv.selection()
        if len(item) == 1 :
            name = item[0]
            if self.lastOpenClose == name :
                self.lastOpenClose = None
                return
            if not (name in self.selectedMulti):
                data = self.items.get(name)
                if data[1] :
                    # dir
                    self.__onDirClicked(name)
                else :
                    # file
                    self.__onFileClicked(name)
                self.selectedMulti = ()
            else :
                self.__changeMulti(name)
        else :
            self.selectedMulti = item
            if len(item) == len(self.items) :
                self.selectedAll = True
        self.lastOpenClose = None

    def __onOpen(self, event):
        items = self.tv.selection()
        self.lastOpenClose = items[0]

    def __onClose(self, event):
        items = self.tv.selection()
        self.lastOpenClose = items[0]

    def __onControlKey(self, event) :
        keysym = event.keysym
        self.__callControlFuncByKey(keysym)

    def __onRightClick(self, event) :
        if self.rightClickFunc :
            items = self.tv.selection()
            self.rightClickFunc(event)            

    def __updateStyles(self) :
        height = self.rowHeight
        size = (height, height)
        self.__releaseIcons()

        font = Font()
        font = Font(size=str(2-height))
        self.style.configure('Treeview', rowheight=height)
        f = pathJoin(THIS_DIR, '../res/%s.png')
        for t in self.tagNames :
            img = GetImgTk(f%(t), size)
            self.__imgs[t] = img
            self.tv.tag_configure(t, image=img, font = font)       

    def __onDestroy(self) :
        self.__releaseIcons()           

    def __onDirClicked(self, name):
        if time.time() - self.timeStamp < 0.5 :
            return
        data = self.items.get(name)
        if data :
            children = self.tv.get_children(name)
            status = data[2]
            if status == 'd_normal' :
                status = 'checked'
            elif status == 'd_part' :   
                status = 'checked'
            elif status == 'd_checked' :
                status = 'normal'

            self.__changeItemStatus(name, status)

    def __onFileClicked(self, name):
        data = self.items.get(name)
        if data :
            status = data[2]
            if status == 'f_normal' :
                status = 'checked'
            elif status == 'f_checked' :
                status = 'normal'

            self.__changeItemStatus(name, status)

    def __changeItemStatus(self, name, status, skipCallback=False) :
        self.__changeTag(name, status)
        self.__updateParentStatus(name)
        if not skipCallback :
            self.__getChoosenFiles()

        self.update_idletasks()

    def __changeTag(self, name, tag, forChild=True) :
        if name == '' :
            return
        t = 'd_'+tag
        if self.isDir(name) :
            # print('__changeTag dir', name, tag)
            names = self.tv.get_children(name)
            if forChild :
                for n in names:
                    self.__changeTag(n, tag)
        else :
            if tag == 'part' :
                return
            t= 'f_'+tag
        self.tv.item(name, tag=[t,])
        self.items[name][2] = t

    def __updateParentStatus(self, name) :
        parent = self.tv.parent(name)
        if parent != '' :
            data = self.items.get(parent)
            if data :
                children = self.tv.get_children(parent)
                checked = None
                for c in children :
                    # if not self.isDir(c) :
                    s = self.items[c][2].split('_')[1]
                    checked = checked or s
                    if (checked is not None and checked != s) or checked == 'part':
                        checked = 'part'
                        break
                self.__changeTag(self.formatPath(parent), checked, False)
                self.__updateParentStatus(parent)

    def __changeMulti(self, iid):
        data = self.items.get(iid)
        status = data[2].find('checked') >= 0 and 'normal' or 'checked'
        for _iid in self.selectedMulti :
            self.__changeTag(_iid, status, False)
        if self.selectedAll :
            self.tv.selection_set(())
            self.selectedMulti = ()
            self.selectedAll = False
        else :
            self.tv.selection_set(self.selectedMulti)
        self.__getChoosenFiles()
        # self.selectedMulti = ()

    def __getChoosenFiles(self, fresh=False) :
        files = []
        needCall = isFunc(self.callback)
        if (not needCall and fresh) or needCall :
            for f in (self.items.values()) :
                if not f[1] and f[2] == 'f_checked' :
                    files.append(f[0])
            files.sort()
            self.choosenFiles = files
            if needCall and not fresh:
                self.callback(files)
        return self.choosenFiles

    def __getUtfStr(self, oriStr, decode='GBK') :
        # TODO:部分不能正常转码
        # s = ''
        # if isFunc(oriStr.decode) :
        #   try:
        #       s = oriStr.decode(decode)
        #   except Exception , e:
        #       s = oriStr.decode('utf-8')
        # s = s.encode('utf-8')
        return oriStr

    def __callControlFuncByKey(self, key):
        f = self.controlFuncs.get(key)
        if isFunc(f) :
            f()

    def __insertItem(self, parent, text, fullPath, isDir, open=False):
        tag = isDir and 'd_normal' or 'f_normal'
        item = self.tv.insert(parent, 'end', text=text, open=open, tags = [tag, ])
        self.items[item] = [fullPath, isDir, tag]
        appDic = self.files
        if isDir :
            appDic = self.dirs
        appDic[fullPath] = item

        return item

    def isDir(self, name) :
        data = self.items.get(name)
        if data :
            return data[1]

    def setRowHeight(self, height) :
        self.rowHeight = height
        self.__updateStyles()

    def setPath(self, path, skip=(r'\.DS_Store',), choosenFiles=[], packages={}) :
        '''参数： path, skip=('\\.DS_Store',), choosenFiles=[], packages={}
        path:           文件夹路径
        skip:           不显示的文件或文件夹，正则匹配字符list 或 tuple，会自动添加^和$进行整个字符串匹配
        choosenFiles:   选中的文件，必须传入 list
        packages:       asb 包名-匹配字符串 字典
        '''
        if path is None :
            return False
        if os.path.isdir(path) :
            if not (isinstance(skip, list) or isinstance(skip, tuple)) :
                ShowInfoDialog(u'skip 必须是正则表达式匹配串组成的 list 或 tuple')
                return False

            self.skipPatterns = [re.compile('^'+p+'$') for p in skip]

            self.packagePatterns = []
            self.packageFiles = {}

            keys = list(packages.keys())
            keys.sort()

            for k in keys :
                self.packagePatterns.append((re.compile('^'+packages.get(k)+'$'), k))

            self.clearItems()
            self.rootPath = path
            self.insertPath(path)

            for k in tuple(self.packageFiles.keys()) :
                self.insert2Package(k, self.packageFiles.get(k))

            self.setChoosenFiles(choosenFiles)

        return self.packageFiles


    def clearItems(self):
        [self.tv.delete(i) for i in self.tv.get_children('')]
        self.items = {}
        self.files = {}
        self.dirs = {}


    def insertPath(self, path, parent='', reverse=False): 
        if parent == '' :
            self.tv.heading('#0', text=path, anchor='w')
            parent = self.__insertItem('', '-------------baseRes-------------', '+baseRes+', True, open=True)

        if self.willFileOrDirSkip(os.path.split(path)[-1]) :
            return 

        files = os.listdir(path)
        if files is not None :
            files.sort(reverse=reverse)
            for p in files : 
                if not self.willFileOrDirSkip(p) :
                    abspath = os.path.join(path, p)
                    abspath = self.formatPath(abspath)
                    isDir = os.path.isdir(abspath)
                    pkg = self.getPackageName(p)
                    if not (pkg and not isDir) :
                        item = self.__insertItem(parent, p, abspath, isDir)

                        if isDir :
                            self.insertPath(abspath, item, reverse)
                    else :
                        arr = self.packageFiles.get(pkg) or []
                        if abspath not in arr :
                            arr.append(abspath)
                        self.packageFiles[pkg] = arr

    def insert2Package(self, pkg, files) :
        text = '-------------packages-------------'
        root = self.dirs.get(text)
        if not root :
            root = self.__insertItem('', text, text, True, open=True)
        
        pkgItem = self.dirs.get(pkg)
        if not pkgItem :
            pkgItem = self.__insertItem(root, pkg, pkg, True)

        for file in files :
            p, s = getRelativePath(file, self.rootPath)
            # self.__insertItem(pkgItem, p, '%s:%s'%(file, pkg), False)
            self.__insertItem(pkgItem, p, file, False)

    def getChoosenFiles(self) :
        return self.__getChoosenFiles(True)

    def setChoosenCallback(self, callback) :
        self.callback = callback

    def setChoosenFiles(self, files) :
        files = list(files)
        if self.rootPath != '' :
            for i in range(len(files)) :
                f = files[i]
                if not os.path.isabs(f) :
                    f = pathJoin(self.rootPath, f)
                    files[i] = self.formatPath(f)
                f = self.formatPath(f)
                item = self.files.get(f) or self.dirs.get(f)
                # if item and not self.isDir(item) :
                # 可以选中文件夹下所有文件
                if item :
                    self.__changeItemStatus(item, 'checked', True)
            for f in set(self.files) - set(files) :
                item = self.files.get(f)
                if item and not self.isDir(item) :
                    self.__changeItemStatus(item, 'normal', True)
        else :
            ShowInfoDialog(u'请先设置根目录再设置已选中的文件！')

    def formatPath(self, path) :
        return path.replace('\\', '/')

    def willFileOrDirSkip(self, name) :
        for p in self.skipPatterns :
            m = p.match(name)
            if m :
                return True
        return False

    def getPackageName(self, name) :
        for p, k in self.packagePatterns :
            if p :
                m = p.match(name)
                if m :
                    return k
        return False

    def selectAll(self) :
        # for k in list(self.items.keys()) :
        #     self.__changeTag(k, 'checked')
        # self.__getChoosenFiles()
        
        # 使用selection_set设置所有会报错，通过遍历的方式设置
        # self.tv.selection_set(self.items.keys())
        for iid in list(self.items.keys()) :
            self.tv.selection_add(iid)
        self.selectedAll = True

    def setRightClickCallback(self, call) :
        self.rightClickFunc = call

    def updateContentSize(self, event) :
        w = event.width
        rw = self.tv.winfo_reqwidth()+150
        # for i in self.items :
        #     bbox = self.tv.bbox(i)
        #     if len(bbox) == 4 :
        #         rw = max(bbox[0]+bbox[2], rw)
        # 设置第一列的宽度，修复水平方向滚动条不显示的bug
        # TODO:最大化之后rw会变很大，之后修复
        self.tv.column("#0", stretch=True, minwidth = rw if rw > w else w)

def __test1(event=None) :
    print('__test1')

def __test2(event=None) :
    print('__test2')

def __main() :

    path = os.getcwd()
    testCall = True

    m = ResExplorer()
    m.pack(expand=YES,fill=BOTH)
    # m.setPath(path, '.manifest', ['D:/Python27/lib/site-packages/TkToolsD/__init__.py', 'D:/Python27/lib/site-packages/TkToolsD/res/d_checked.png', 'D:/Python27/lib/site-packages/TkToolsD/res/d_normal.png', 'D:/Python27/lib/site-packages/TkToolsD/res/f_checked.png', 'D:/Python27/lib/site-packages/TkToolsD/res/f_normal.png'])
    # m.setPath(path, '.manifest', ['__init__.py', 'res/d_checked.png', 'res/d_normal.png', 'res/f_checked.png', 'res/f_normal.png'])
    ret = m.setPath(path, (r'\.DS_Store', '__.*'), [], {'png':r'.*\.png', 'pyc':r'.*\.pyc'})
    # ret = m.setPath(path)
    if not ret :
        return
    # m.setChoosenFiles(['D:/Python27/lib/site-packages/TkToolsD/CommonWidgets.py',])
    # m.setChoosenFiles(['/Users/sjytyf3/Documents/Dekiven/GameResUploadTools/src/AppFrame.py',])
    m.setChoosenFiles(['ResExplorer.py',])
    if testCall :
        def callbcak (files) :
            print(u'test 输出')
            print(files)
        m.setChoosenCallback(callbcak)
    else :
        def cmd () :
            print(m.getChoosenFiles())
        ttk.Button(text='test', command=cmd).pack()

    root = getToplevel(m)
    conf = (
        (u'文件', (
                ('1-1', __test1, '<Escape>', u'关闭'),
                ('1-2', __test2),
                'line', # 任意不是 function、list、tuple 的值都会添加一条分割线
                ('3', (
                        ('3-1', __test1),
                        ('3-2', __test2),
                    )
                ),
            ) 
        ),
        ('2', (
                ('2-1', __test1,),
                ('2-2', __test2, 'Ce'),
            ) 
        ),
    )

    def onRightClick(event=None) :
        if event :
            menu = getMenu(m, *conf)
            menu.post(event.x_root, event.y_root)

    m.setRightClickCallback(onRightClick)

    m.mainloop()

if __name__ == '__main__':
    __main()
    # a, b = getHotKeyCommandName('CSa')
    # print(a)
    # print(b)

