# -*- coding:utf-8 -*- 
# Date: 2018-03-28 09:44:17
# Author: dekiven

from src.AppFrame import AppFrame 
from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *

tk, ttk = getTk()

def initUI() :
	root = tk.Tk()

	app = AppFrame(root)
	app.loadConfigs('config/projConfig.json')
	app.pack(fill=tk.BOTH, expand=True)
	centerToplevel(app)
	app.focus_set()
	root.mainloop()

def main() :
	initUI()

if __name__ == '__main__':
	main()

