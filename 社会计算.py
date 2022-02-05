# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 13:40:26 2020

@author: 28567
"""
from collections import defaultdict
import jieba.analyse
import os
import jieba
import jieba.posseg as pseg
import re
import codecs

fd=open("外卖评论.csv",'rb').read()
rt=open("hit_stopwords.txt",'rb')
seg_list = jieba.cut(fd)
seg = jieba.cut(fd)
segs=jieba.lcut(fd)
print("Paddle Mode: " + '/'.join(list(seg_list)))
tags=jieba.analyse.extract_tags(fd)
print(",".join(tags))
full_path1="分词结果"+'.txt'
file1=open(full_path1,'a',encoding='utf-8')
file1.write('/'.join(segs))
file1.close()
words = pseg.cut(fd,use_paddle=True)#词性划分
newSent = []
x=0
y=1
r=0
z=1
for word in segs:
     p(word)=0
     pb(word)=1
     if(word!='0000'&word!=):#标准词
       while(segs[x]!=null):
         if(segs[x]=='1')
            z=1
         if(segs[x]=='0')
            z=-1
         if(segs[x]==)#标准词
            r=1
         if(segs[x]==&y=1）#标准词#
            p(word)+=z
            x++
            continue
         if(segs[x]=='\n'):
            y=0
            r=0
            x++
            continue
         if(segs[x]==word&r==1):
            y=1
            p(word)+=z
            segs[x]='0000'
            x++
            continue
         if(seg[x]==word)
            y=1
            seg[x]='0000'
            pb(word)++
            x++
            continue
         x++
       
         
         
     
            
file=open("123.txt",'a',encoding='utf-8')
file.write('/'.join(newSent))
file.close()