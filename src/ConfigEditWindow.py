# -*- coding:utf-8 -*-
# 创建时间：2019-03-25 11:47:32
# 创建人：  Dekiven

import os
from TkToolsD.CommonWidgets import *
from TkToolsD.ConfigEditor import ConfigEditor

tk, ttk = getTk()
# help(tk.Event)

class ConfigEditWindow(tk.Toplevel) :
    '''ConfigEditWindow
    '''
    def __init__(self, *args, **dArgs) :
        tk.Toplevel.__init__(self, *args, **dArgs)

        notebook = ttk.Notebook(self)
        notebook.pack(expand=tk.YES, fill=tk.BOTH)
        notebook.bind('<<NotebookTabChanged>>', self.__onChangeTab)

        self.notebook = notebook

        self.frames = []
        self.data = {}
        self.platforms = []
        self.curIdx = 0
        self.callback = None

        self.geometry('600x400')

    def setData(self, data, platforms) :
        self.data = data
        for name in platforms :
            self.__addFrame(name, data.get(name) or {})

    def setCallback(self, callback) :
        self.callback = callback

    def __addFrame(self, name, conf) :
        notebook = self.notebook
        frame = ttk.LabelFrame(notebook, text=name, width=400)
        cmv = ConfigEditor(frame)
        cmv.pack(expand=tk.YES, fill=tk.BOTH)
        cmv.setSupportTypes(('int', 'float', 'bool', 'string', 'version'))
        cmv.setData(conf)

        def __onChange(d) :
            self.data[name] = d
            if self.callback :
                self.callback(name, d)

        cmv.setCallback(__onChange)

        notebook.add(frame, text=name)

    def __onChangeTab(self, event):
        notebook = self.notebook
        self.curIdx = notebook.index('current')

def __main() :
    root = tk.Tk()
    c = ConfigEditWindow(root)

    c.setData({'a':{
        'test1':('string', 'test1str',),
        'testDic':('dict', {
            'a':('string', 'aStr'),
            'b':('string', 'bStr'),
            't':('dict', {
                'a':('string', 'aStr'),
                'b':('string', 'bStr'),
            }),
        }),
        'testList':('list', (('string', 'list1'), ('int', 1)))
    }}, ['a', 'b'])

    def p(n, d) :
        print(n, d)

    c.setCallback(lambda n,d: p(n,d))
    centerToplevel(c)
    root.wait_window()
    root.mainloop()

if __name__ == '__main__' :
    __main()
