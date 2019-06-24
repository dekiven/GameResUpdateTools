# -*- coding:utf-8 -*-
# 创建时间：2019-06-14 16:35:00
# 创建人：  Dekiven

import os
from TkToolsD.CommonWidgets import *
from TkToolsD.ConfigEditor import ConfigEditor

tk, ttk = getTk()

class AsbPackageWindow(tk.Toplevel) :
    '''asb分包包名管理界面
    '''
    def __init__( self, *args, **dArgs ) :
        tk.Toplevel.__init__(self, *args, **dArgs)

        self.callback = None

        cmv = ConfigEditor(self)
        cmv.pack(expand=tk.YES, fill=tk.BOTH)
        cmv.setSupportTypes(('string', ))

        def __onChange(d) :
            self.data = d
            if isFunc(self.callback) :
                self.callback(d)

        cmv.setCallback(__onChange)

        self.cmv = cmv
        
        self.geometry('600x400')

    def setData(self, data) :
        self.data = data
        self.cmv.setData(data)
    
    def setCallback(self, callback) :
        self.callback = callback

def __main() :
    root = tk.Tk()
    c = AsbPackageWindow(root)

    c.setData({'cn':('string', r'\S+\.cn')})

    def p(d) :
        print(d)

    # c.setCallback(lambda d: p(d))
    centerToplevel(c)
    # root.wait_window()
    root.mainloop()

if __name__ == '__main__' :
    __main()
