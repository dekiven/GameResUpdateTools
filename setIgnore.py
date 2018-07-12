import os
from DKVTools.Funcs import *

ignoreList = [
    '*.pyc',
    'config/',
]

f = open('.gitignore', 'w')

for i in ignoreList :
    f.write(i+'\n')
    
f.close()