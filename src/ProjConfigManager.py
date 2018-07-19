# -*- coding:utf-8 -*- 
# Date: 2018-03-28 11:27:16
# Author: dekiven

import os
import json

from DKVTools.Funcs import *

#import sys 
#reload(sys)
#sys.setdefaultencoding('utf-8')
key_projs = 'projs'
key_cur_proj = 'curProj'

class ProjConfigManager(object) :
	'''ProjConfigManager
	'''
	def __init__(self, path) :
		super(ProjConfigManager, self).__init__()
		self.path = None
		self.conf = {key_projs:{}, key_cur_proj:''}
		self.__initPath(path)
		self.loadConfig()

	def __initPath(self, path) :
		if not os.path.isabs(path) :
			path = pathJoin(getMainCwd(), path)
		self.path = path

		if not os.path.isfile(path) :
			pd = os.path.dirname(path)
			if not os.path.isdir(pd) :
				os.makedirs(pd)
			self.saveConfig()
			# f = open(path, 'w')
			# f.write('{key_projs:{}, "curProj":""}')
			# f.close()

	def loadConfig(self):
		# import DKVTools
		# help(DKVTools.Funcs)
		f = open(self.path, 'rb')
		jsonStr = bytes2utf8Str(f.read())
		f.close()

		self.conf = json.loads(jsonStr, encoding='utf-8')

	def saveConfig(self):
		# jsonStr = json.dumps(self.conf, sort_keys=True, indent=4, encoding='utf-8')
		jsonStr = ''
		if isPython3() :
			jsonStr = json.dumps(self.conf, indent=4)
		else :
			jsonStr = json.dumps(self.conf, indent=4, encoding='utf-8')
		f = open(self.path, 'w')
		f.write(jsonStr)
		f.close()


	def getProjConfig(self, pName, key=None):
		conf =  self.conf[key_projs].get(pName)
		if key is None :
			return conf
		else :
			return conf.get(key)

	def addProj(self, pName, data={}):
		if self.getProjConfig(pName) is None :
			self.conf[key_projs][pName] = data


	def changeProjConfig(self, pName, key, value):
		'''修改项目配置，项目存在返回True，不存在返回False'''
		conf = self.getProjConfig(pName)
		if conf is not None:
			conf[key] = value
			return True
		else :
			return False

	def getProjNames(self) :
		names = list(self.conf[key_projs].keys())
		names.sort()
		return names

	def setCurProj(self, pName) :
		self.conf[key_cur_proj] = pName

	def getCurProjName(self) :
		return self.conf[key_cur_proj]

def main() :
	print(ProjConfigManager.__doc__)
	c = ProjConfigManager('test.json')
	

if __name__ == '__main__':
	main()

