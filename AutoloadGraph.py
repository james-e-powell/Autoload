import time
import sys
import os
import io

class AutoloadGraph:
   __authorNodeColumns = 'objectId:ID,name,:LABEL\n'
   __publicationNodeColumns = 'objectId:ID,name,title,date,:LABEL\n'
   __fileNodeColumns = 'objectId:ID,name,score,:LABEL\n'
   __publisherNodeColumns = 'objectId:ID,issn,name,:LABEL\n'
   __subjectNodeColumns = 'objectId:ID,name,:LABEL\n'
   __edgeColumns = ':START_ID,:END_ID,:TYPE\n'
   idCounter = 0

   def __init__(self,graphDir='grapTesthDir'):
      print 'initializing object instance'
      print graphDir
      self.nodes = {}
      self.nodesOutput = []
      self.nodeList = []
      self.edges = []

      now = time.localtime(time.time())
      nowSuffix = str(now.tm_year) + str(now.tm_mday) + str(now.tm_mon) + str(now.tm_hour) + str(now.tm_min)

      self.authorNodeFile = './' + graphDir + '/autoload_nodes_author_' + nowSuffix + '.csv'
      self.initializeFile(self.authorNodeFile, self.__authorNodeColumns)

      self.publicationNodeFile = './' + graphDir + '/autoload_nodes_publication_' + nowSuffix + '.csv'
      self.initializeFile(self.publicationNodeFile, self.__publicationNodeColumns)

      self.subjectNodeFile = './' + graphDir + '/autoload_nodes_subject_' + nowSuffix + '.csv'
      self.initializeFile(self.subjectNodeFile, self.__subjectNodeColumns)

      self.publisherNodeFile = './' + graphDir + '/autoload_nodes_publisher_' + nowSuffix + '.csv'
      self.initializeFile(self.publisherNodeFile, self.__publisherNodeColumns)

      self.fileNodeFile = './' + graphDir + '/autoload_nodes_file_' + nowSuffix + '.csv'
      self.initializeFile(self.fileNodeFile, self.__fileNodeColumns)

      self.edgeFile = './' + graphDir + '/autoload_edges_' + nowSuffix + '.csv'
      self.initializeFile(self.edgeFile, self.__edgeColumns)

   def __del__(self):
      class_name = self.__class__.__name__
      print class_name, "destroyed"

   def getIdCounter(self):
      return self.idCounter

   def incrementIdCounter(self):
      self.idCounter +=1
      return self.idCounter

   def addNode(self, nodeKey, nodeVal, properties):
     self.nodes[nodeVal]=self.idCounter
     self.nodeList.append(nodeKey)
     self.incrementIdCounter()
     nodeString = nodeKey + ',' + nodeVal
     self.nodesOutput.append(nodeString)
     self.appendToFile('node',nodeString)


   def addEdge(self, edgeString):
     self.edges.append(edgeString)
     self.appendToFile('edge', edgeString)

   def appendNodeToFile(self, type, value):
     # append to node file

     if type=='author':
       with open(self.authorNodeFile, 'a') as file:
         file.writelines(value)
         file.flush()
       file.close()

     if type=='publication':
       with open(self.publicationNodeFile, 'a') as file:
         file.writelines(value)
         file.flush()
       file.close()

     if type=='publisher':
       with open(self.publisherNodeFile, 'a') as file:
         file.writelines(value)
         file.flush()
       file.close()

     if type=='subject':
       with open(self.subjectNodeFile, 'a') as file:
         file.writelines(value)
         file.flush()
       file.close()

     if type=='file':
       with open(self.fileNodeFile, 'a') as file:
         file.writelines(value)
         file.flush()
       file.close()
 
   def appendEdgeToFile(self, value):
       # append to edge
       with open(self.edgeFile, 'a') as file:
         file.writelines(value)
         file.flush() 
       file.close() 

   def initializeFile(self, filename, columnHeaders):
       with open(filename, 'w') as file:
         file.writelines(columnHeaders)
       file.close()
   
