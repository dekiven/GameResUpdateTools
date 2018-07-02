# -*- coding:utf-8 -*- 
# Date: 2018-03-28 09:52:31
# Author: dekiven

try:
	import TkToolsD
except Exception as e:
	import os
	rst = os.popen('pip install TkToolsD')
	print(rst.read())