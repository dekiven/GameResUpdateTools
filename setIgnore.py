import os
from DKVTools.Funcs import *

ignoreList = [
    '*.pyc',
    'config/',
    'wheels',
]

f = open('.gitignore', 'w')

for i in ignoreList :
    f.write(i+'\n')
    
f.close()