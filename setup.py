#!/usr/bin/env python

from distutils.core import setup

setup(name='python-mongodb-chs-indexer',
      version='0.02',
      description='简易的MongoDB全文索引引擎',
      author='Samuel Cui',
      author_email='i@samcui.com',
      url='http://samcui.com/',
      packages=['mongodb_indexer'],
      requires=['jieba', 'pymongo', 'tornado_tilimer']
     )