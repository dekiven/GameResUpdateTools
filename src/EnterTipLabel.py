# -*- coding:utf-8 -*- 
# Date: 2018-04-02 15:11:58
# Author: dekiven

import os

from DKVTools.Funcs import *
from TkToolsD.CommonWidgets import *

if isPython3() :
	import tkinter as tk
	from tkinter import ttk 

else :
	import Tkinter as tk
	import ttk

class __ToolTip(object):
	def __init__(self, widget):
		self.widget = widget
		self.tipwindow = None
		self.x = self.y = 0

	def showtip(self, **labelConfig):
		"Display text in tooltip window"
		if self.tipwindow :
			return
		x, y, _cx, cy = self.widget.bbox("insert")
		x = x + self.widget.winfo_rootx()
		y = y + cy + self.widget.winfo_rooty() - 50
		self.tipwindow = tw = tk.Toplevel(self.widget)
		tw.wm_overrideredirect(1)
		tw.wm_geometry("+%d+%d" % (x, y))

		keys = list(labelConfig.keys())

		if 'bg' not in keys and 'background' not in keys :
			labelConfig['bg'] = '#aaaaff'
		label = tk.Label(tw, **labelConfig)
		label.pack(ipadx=1)

	def hidetip(self):
		tw = self.tipwindow
		self.tipwindow = None
		if tw:
			tw.destroy()

def regEnterTip(widget, **labelConfig) :
	toolTip = __ToolTip(widget)
	def enter(event):
		toolTip.showtip(**labelConfig)
	def leave(event):
		toolTip.hidetip()
	widget.bind('<Enter>', enter)
	widget.bind('<Leave>', leave)



def main() :
	print(EnterTipLabel.__doc__)
	

if __name__ == '__main__':
	main()

