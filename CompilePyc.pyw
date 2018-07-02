# -*- coding:utf-8 -*- 
# Date: 2018-04-03 09:04:21
# Author: dekiven

import os
import py_compile
from DKVTools.Funcs import *


zipP = 'E:\u3dProj\GameResTools.zip'

def __main() :
	curDir = os.getcwd()
	for _dir, folders, files in os.walk(curDir) :
		for f in files :
			if f[-3:] == '.py' :
				py_compile.compile(os.path.join(_dir, f))

	zipFolder(os.getcwd(), zipP, suffixs='.pyc,.pyw,.bat,.command', skipFiles=('Demo.pyw', 'CompilePyc.pyw'))
	os.startfile(os.path.dirname(zipP or curDir))

if __name__ == '__main__':
	__main()

