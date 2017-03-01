import sys
import re
import math
from numpy import zeros,dot
from numpy.linalg import norm
import porter


class Compare:
   score = 0
   doc1 = ''
   doc2 = ''
   __splitter=re.compile ( "[a-zA-Z\-']+", re.I )
   __stemmer=porter.PorterStemmer()

   def __del__(self):
      class_name = self.__class__.__name__
      print class_name, "destroyed"

   def setDoc1(self, doc1):
     self.doc1 = doc1

   def setDoc2(self, doc2):
     self.doc2 = doc2

   def add_word(self,word,d):
     """
       Adds a word the a dictionary for words/count
       first checks for stop words
       the converts word to stemmed version
     """
     w=word.lower() 
     # if w not in stop_words:
     # ws=stemmer.stem(w,0,len(w)-1)
     ws = w
     d.setdefault(ws,0)
     d[ws] += 1

   def doc_vec(self,doc,key_idx):
     v=zeros(len(key_idx))
     for word in self.__splitter.findall(doc):
       # keydata=key_idx.get(stemmer.stem(word,0,len(word)-1).lower(), None)
       keydata=key_idx.get(word.lower(), None)
       # if keydata: v[keydata[0]] = 1
       if keydata: v[keydata[0]] += 1
     return v

   def compare(self):
     # strip all punctuation but - and '
     # convert to lower case
     # store word/occurance in dict
     all_words=dict()

     for dat in [self.doc1,self.doc2]:
       [self.add_word(w,all_words) for w in self.__splitter.findall(dat)]
 
     # build an index of keys so that we know the word positions for the vector
     key_idx=dict() # key-> ( position, count )
     keys=all_words.keys()
     keys.sort()
     for i in range(len(keys)):
       key_idx[keys[i]] = (i,all_words[keys[i]])
     del keys
     del all_words

     v1=self.doc_vec(self.doc1,key_idx)
     v2=self.doc_vec(self.doc2,key_idx)
     # return math.acos(float(dot(v1,v2) / (norm(v1) * norm(v2))))
     # return math.acos(float(dot(v1,v2) / (norm(v1) * norm(v2)))) 
     try:
       degreeScore = math.degrees(math.acos(float(dot(v1,v2) / (norm(v1) * norm(v2)))))
     except:
       degreeScore = 0 
     return degreeScore

