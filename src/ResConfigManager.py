# -*- coding:utf-8 -*- 
# Date: 2018-03-29 10:51:32
# Author: dekiven

import os
import json
import re

from DKVTools.Funcs import *
#import sys 
#reload(sys)
#sys.setdefaultencoding('utf-8')
configFileName = 'resConf.bytes'
historyFileName = 'history.json'
crcConfExt = '.manifest'

class ResConfigManager(object) :
	'''ResConfigManager
	'''
	def __init__(self, path, version='0.0.0', outPath=None, testMode=False) :
		super(ResConfigManager, self).__init__()
		self.path = None
		self.platform = None
		self.outPath = outPath
		self.testMode = testMode
		# 读取的配置
		# 可修改的配置
		self.history = {'versions':[], 'log':{}}
		self.conf = {'version':version, 'files':{}}
		self.__initPath(path)
		self.loadConfig()
		self.pattenCRC = re.compile('^\s*CRC:\s*(\d+)\s*$')

	def __initPath(self, path) :
		self.platform = os.path.split(path)[-1]
		# print(self.platform)
		if not os.path.isabs(path) :
			path = pathJoin(getMainCwd(), path)
		path = path.replace('\\', '/')
		self.path = path
		if self.outPath is None :
			self.outPath = path
		if not os.path.isdir(path) :
			os.makedirs(path)
		fp = self.__getHitoryPath()
		if not os.path.isfile(fp) :
			# pd = os.path.dirname(path)
			self.saveConfig(False, True)

	def __getCurVerPath(self):
		return pathJoin(self.path, configFileName)

	def __getHitoryPath(self) :
		return pathJoin(self.path, historyFileName)

	def setVersion(self, v) :
		self.conf['version'] = v

	def loadConfig(self):
		# fp = self.__getCurVerPath()
		# f = open(fp, 'rb')
		# jsonStr = f.read().encode('utf-8')
		# f.close()
		# self.conf = json.loads(jsonStr, encoding='utf-8')
		fp = self.__getHitoryPath()
		f = open(fp, 'rb')
		jsonStr = f.read().encode('utf-8')
		f.close()
		self.history = json.loads(jsonStr, encoding='utf-8')

	def saveConfig(self, cur=True, history=False):
		if cur :
			self.saveCurVer()
		if history :
			self.saveHistroy()

	def saveHistroy(self) :
		fp = self.__getHitoryPath()
		jsonStr = json.dumps(self.history, indent=4, encoding='utf-8')
		f = open(fp, 'w')
		f.write(jsonStr)
		f.close()

	def saveCurVer(self, path=None):
		fp = path or self.__getCurVerPath()
		# jsonStr = json.dumps(self.conf, sort_keys=True, indent=4, encoding='utf-8')
		f = open(fp, 'w')
		f.write('version|%s\n'%(self.conf['version']))
		for fn in tuple(self.conf['files'].keys()) :
			size = os.path.getsize(pathJoin(self.path, fn))
			f.write('%s|%s|%d\n'%(fn, self.conf['files'][fn], size))
		# f.write(jsonStr)
		f.close()

	def readResInfo(self, path) :
		f = open(path, 'rb')
		lines = f.readlines()
		# content = r.read().encode('utf-8')
		f.close()

		l = lines[1].encode('utf-8')
		m = self.pattenCRC.match(l)
		if m :
			crc = m.group(1)
			p = self.getRelativePath(path).replace(crcConfExt, '')
			# print(p, crc)
			return (p, crc)

	def getCurResInfos(self, path=None) :
		data = []
		path = path or self.path
		for _dir, folders, files in os.walk(path) :
			for f in files :
				ext = os.path.splitext(f)[-1]
				if ext == crcConfExt :
					p = pathJoin(_dir, f)
					data.append(self.readResInfo(p))
		files = dict(data)
		self.conf['files'] = files
		# print(files)
		return files.copy()


	def getRelativePath(self, p) :
		p = p.replace('\\', '/')
		path = self.path
		if os.path.isabs(p) and len(p) > len(path) :
			l = len(path)+1
		return p[l:]

	def getChangedInfo(self, diffFrom=None) :
		orifiles = {}
		for v in self.history['versions'] :
			if diffFrom is None or v != diffFrom :
				for f,crc in self.history['log'][v].items() :
					orifiles[f] = crc
			else :
				break

		files = self.getCurResInfos()
		for f, crc in files.items() :
			if crc == orifiles.get(f) :
				# 删除相同的文件
				del files[f]

		return files

	def addLog(self, version, files) :
		versions = self.history['versions']
		# 测试模式不记录历史
		if not version in versions and len(list(files.keys())) > 0 and not self.testMode :
			self.history['versions'].append(version)
			self.history['log'][version] = dict(files)
		self.saveConfig(False, True)

	def saveBaseResConfig(self, files, configPath) :
		fp = self.__getCurVerPath()
		f = open(fp, 'rb')
		lines = f.readlines()
		f.close()
		version = lines[0].decode('utf-8').split('|')[1].strip()
		sFiles = {}
		for l in lines[1:] :
			l = l.decode('utf-8')
			sp = l.split('|')
			sFiles[sp[0].strip()] = sp[1].strip()
		_files = {}
		for f in files :
			crc = sFiles.get(f)
			if crc is not None :
				_files[f] = crc
			else :
				# raise Exception('"%s" has ben choosen but do not in version'%(f))
				# print('"%s" has ben choosen but do not in version'%(f))
				# TODO:show log 
				pass
		conf = {}
		conf['version'] = version + '.base'
		conf['files'] = _files
		self.conf = conf
		self.saveCurVer(configPath)


def main() :
	version = '0.0.2'
	res = ResConfigManager('pc', version)
	# res.getCurResInfos()
	# res.saveConfig()
	# res.addLog('0.0.2', {'f1':'12345',})
	change = res.getChangedInfo()
	res.addLog(version, change)
	res.saveConfig()
	# TODO:zip and upload
	print('finished!')

if __name__ == '__main__':
	main()

