# -*- coding:utf-8 -*- 
# Date: 2018-03-28 15:31:40
# Author: dekiven

import os

from DKVTools.Funcs import *

if isPython3() :
	import tkinter as tk  
	from tkinter import ttk 	
	from tkinter import Spinbox  
else :
	import Tkinter as tk  
	import  ttk
	from Tkinter import Spinbox  
	
#import sys 
#reload(sys)
#sys.setdefaultencoding('utf-8')

class VersionWidget(ttk.Frame) :
	'''VersionWidget
	'''
	def __init__(self, *args, **dArgs) :
		ttk.Frame.__init__(self, *args, **dArgs)
		self.callback = None
		self.verLen = 3
		self.spinboxArr = []
		self.minVersion = (0,0,0)

		self.columnconfigure(0, weight=1)

		curVerLabel = ttk.Label(self)
		curVerLabel.grid(sticky='nswe')
		self.curVerLabel = curVerLabel


		for i in range(0, self.verLen) :
			self.__getSpinbox(i)

		self.setCurVersion((0,0,0))

	def __getSpinCallback(self, sp, index) :
		param = [sp, index]
		def func() :
			self.__onSpin(*param)

		return func

	def __getSpinbox(self, i) :
		sv = tk.StringVar()
		sb = Spinbox(self, from_=0, to=999, width=5, textvariable=sv)
		sb.configure(command=self.__getSpinCallback(sb, i))
		# 版本信息前有个label
		sb.grid(column=i+1, row=0)
		sb.get = sv.get
		sb.set = sv.set
		if i >= len(self.spinboxArr) :
			self.spinboxArr.append(sb)

	def __hideSpinbox(self, i) :
		if i < len(self.spinboxArr) :
			sb = self.spinboxArr[i]
			sb.gird_remove()

	def __onSpin(self, spinbox, idx) :
		for i in range(idx+1, self.verLen) :
			sb = self.spinboxArr[i]
			if sb :
				sb.set(0)
		self.__checkVersioAvailable()
		callback = self.callback
		if callback :
			callback(self.getVersion())
	
	def __checkVersioAvailable(self) :
		if self.getVersionTuple() < tuple(self.minVersion) :
			self.setVertion(self.minVersion)

	def setCurVersion(self, version) :
		verStr = None
		# verArr = []
		if isinstance(version, list) or isinstance(version, tuple) :
			verStr = '.'.join([str(i) for i in version])
			# verArr = version
		# elif isinstance(version, str):
		else :
			verStr = version
			# verArr = version.split('.')
		# minVersion = [int(v) for v in verArr]
		# minVersion[-1] += 1
		self.setMinVersion(version)
		self.curVerLabel.configure(text=u'当前版本:%s \t新版本:'%(verStr))

	def setVertion(self, version) :
		verArr = None
		if isinstance(version, list) or isinstance(version, tuple) :
			verArr = version
		elif isinstance(version, str):
			verArr = version.split('.')
		if verArr :
			i = 0
			for sb in self.spinboxArr :
				if len(verArr) > i :
					sb.set(verArr[i])
				else :
					sb.set(0)
				i+=1

	def setMinVersion(self, minVersion) :
		minv = None
		if isinstance(minVersion, list) or isinstance(minVersion, tuple) :
			minv = minVersion
		# elif isinstance(minVersion, str):
		else :
			minv = [int(i) for i in minVersion.split('.')]
		self.minVersion = minv or self.minVersion
		self.__checkVersioAvailable()

	def getVersionTuple(self) :
		nl = []
		for i in range(0, self.verLen) :
			sb = self.spinboxArr[i]
			nl.append(int(sb.get()))
		return tuple(nl)

	def getVersion(self) :		
		return '.'.join([str(i) for i in self.getVersionTuple()])

	def setCallback(self, callback) :
		self.callback = callback
		
	def getMinVersion(self) :
		return self.minVersion

	def setVersionLen(self, l) :
		if l > self.verLen :
			for i in range(self.verLen, l) :
				self.__getSpinbox(i)
		elif self.verLen > l :
			for i in range(l, self.verLen) :
				self.__hideSpinbox(i)
		self.verLen = l

	def hasVersionChanged(self):
		return self.getVersionTuple() > tuple(self.minVersion)

def main() :
	v = VersionWidget()
	v.grid()
	v.setVertion('1.1.9')
	v.setMinVersion((1,2,4))
	print(v.getVersionTuple())
	print(v.getVersion())
	v.mainloop()

if __name__ == '__main__':
	main()

