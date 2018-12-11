# -*- coding:utf-8 -*- 
# Date: 2018-03-28 09:44:17
# Author: dekiven

from src.AppFrame import AppFrame 
from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *
if isPython3() :
	import tkinter as tk  
	from tkinter import ttk 	
else :
	import Tkinter as tk  
	import  ttk

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

