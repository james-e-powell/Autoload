import csv
import re
import os
import sys
import string
import requests
import urllib
import uuid
from random import randint
from time import sleep
from bs4 import BeautifulSoup
from xml.dom import minidom
import xmltodict

# 1. retrieve resource or change list as per command line
# 2. iterate through the <loc> elements, if there is a described and a reciprocal describes, then skip it
# 3. if it is only metadata (describes), then request metadata in XML format from aDORe
# 4. if there is a doi element in the metadata from aDORe, continue, otherwise skip this entry
# 5. request metadata for this DOI from Crossref if it is not already in the Crossref directory
# 6. request oaDOI metadata from oaDOI service if a record is not present in the oaDOI directory
# 7. look for a freetext_uri key in this file and extract the URI if it is present
# 8. try to determine via HEAD if the URI from oaDOI is a PDF
# 9. if it is not a PDF, then send this URI on to the recursive screen scraper
# 10. if it is a PDF, retrieve and store the file
# 11. if there is no freetext_uri or no response from oaDOI, resolve this DOI via a DOI resolver
# 12. use the response from the DOI resolver with the recursive screen scraper
# 13. wait for the screen scraper to run to completion
# 14. check to see if there is a SHERPA/RoMEO record for the ISSN that occurs in the Crossref record for this item
# 15. if there is one, proceed to the next entry in the resource sync list
# 16. if there is not, retrieve details about license via the SHERPA/RoMEO API and store them
# 17. once the resource sync list is exhausted, build or rebuild the property graph node and edge csv files
# 18. import the graph
# 19. done.

class Harvester:
  # This is an aggressive PDF harvester class for publications 
  __fileStoreDir = './pdfs/'
  __http_proxy  = 'http://proxyout.lanl.gov:8080'
  __https_proxy  = 'http://proxyout.lanl.gov:8080'
  doi = '' # the DOI for this item
  startUri = '' # a URI from a DOI/oaDOI resolver 
  contentType = 'application/pdf' # will usually be application/PDF, but reserve ability to change it
  filePattern = 'pdf' # will usually be pdf, but reserve ability to change it
  anchorTextPattern = 'full text'
  fileList = {} # all the files that have been discovered and saved, filename, contents of

  def setDoi(self,doi):
    self.doi = doi

  def setStartUri(self,startUri):
    self.startUri = startUri

  def setContentType(self,contentType='application/pdf'):
    self.contentType = contentType

  def setFilePattern(self,filePattern='pdf'):
    self.filePattern=filePattern

  def setStoreDir(self,dir):
    self.__fileStoreDir = dir

  def setAnchorTextPattern(self,anchorTextPattern='full text'):
    self.anchorTextPattern=anchorTextPattern

  def getUri(self, resourceUri):
    print 'getting ' + resourceUri
    user_agent = {'User-agent': 'Mozilla/5.0'}
    resp = requests.get(resourceUri, headers=user_agent, allow_redirects=True)
    print 'request done'
    return resp

  def getProxiedUri(self, resourceUri):
    proxyDict = {
              "https" : self.__https_proxy,
              "http"  : self.__http_proxy
              }
    print 'getting ' + resourceUri
    user_agent = {'User-agent': 'Mozilla/5.0'}
    resp = requests.get(resourceUri, headers=user_agent, allow_redirects=True, proxies=proxyDict)
    print 'request done'
    return resp

  def saveHeader(fileContents):
    uuidFilename = uuid.uuid4()
    print 'Saving as ' + str(uuidFilename)
    doiAsFilename = self.doi.replace('/','_')
    fullPath = self.__fileStoreDir + doiAsFilename + '/header:' + str(uuidFilename)
    print fullPath
    if not os.path.exists(os.path.dirname(fullPath)):
      try:
        os.makedirs(os.path.dirname(fullPath))
      except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
          raise
    with open(fullPath, 'w') as fe:
        fe.write(fileContents)
        fe.flush()
    fe.close()
    print 'Retrieved file written as ' + str(uuidFilename)

  def makeHeaderString(uriRetrieveResponse) :
    headerBuffer = ''
    headerBuffer = 'URL : ' + uriRetrieveResponse.url + '\n'
    try:
      headerBuffer += 'STATUS : ' + uriRetrieveResponse.status_code + '\n'
    except:
      pass
    for header in uriRetrieveResponse.headers:
      headerBuffer+= header + ' : ' + uriRetrieveResponse.headers[header] + '\n'
    print headerBuffer
    return headerBuffer

  def fixPdfFilename(filename):
    newFilename = filename
    if self.filePattern in filename and not filename[-3:]==self.filePattern:
      try: 
        parts=filename.split('.' + self.filePattern)
        newFilename = parts[0]+'.' + self.filePattern
        print 'Fixed ' + self.filePattern + ' filename is ' + newFilename
      except:
        pass
    print newFilename
    return newFilename

  def browsingPause(self):
     pauseFor = randint(10,30)
     print 'Pausing for ' + str(pauseFor) + ' seconds'
     sleep(pauseFor)

  def readingPause(self):
     pauseFor = randint(45,120)
     print 'Pausing for ' + str(pauseFor) + ' seconds'
     sleep(pauseFor)

  def parseForLinks(self, contents, linksList, nextUri):
   
    try:
      print 'parsing'
      soup = BeautifulSoup(contents, "lxml")
      links = soup.find_all("a")
      print 'Going one level deeper... '
      self.browsingPause()
      baseUrl = nextUri
      print 'This is the baseUrl value: ' + baseUrl

      try: 
        print 'looking for iframes ...'
        iframes = []
        iframes = soup.find_all('iframe')
        print str(len(iframes))
        for iframe in iframes:
          srcLink = iframe["src"]
          print 'iframe src ' + srcLink
          if self.filePattern in srcLink:
            print self.filePattern +' file found'
            doiAsFilename = doi.replace('/','_')
            print doiAsFilename
            saveFilename = ''
            try:
              urlSplit = thisLink.split('/')
              saveFilename = urlSplit[-1].lower()
            except:
              saveFilename = thisLink
            saveFilename = fixPdfFilename(saveFilename)
            print saveFilename
            fullPath = self.__fileStoreDir + doiAsFilename + '/' + saveFilename
            print 'saving to ' + fullPath
            if not os.path.exists(os.path.dirname(fullPath)):
              try:
                os.makedirs(os.path.dirname(fullPath))
              except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                  raise
            with open(fullPath, 'wb') as fe:
                fe.write(fileRequest.content)
                fe.flush()
            fe.close()
            idCounter = appendFileToGraph(doi,fullPath, idCounter)
            print 'Retrieved ' + self.filePattern + ' file written as ' + saveFilename
      except:
         pass
  
      print 'examining page links ... '
      for link in links:
        thisLink = link["href"]
        thisLinkText = link.get_text().lower()
        if not 'http' in thisLink:
          if thisLink[0]=='/':
            thisLink=thisLink[1:]
          thisLink = baseUrl + thisLink
        if not thisLink in linksList:
          linksList.append(thisLink)
          if self.filePattern in thisLink or self.filePattern in thisLinkText or self.anchorTextPattern in thisLinkText:
            print 'Preparing to get file link: ' + thisLink
            print 'Anchor text for this link : ' + thisLinkText
            try:
              fileRequest = self.getProxiedUri(thisLink)
              print 'file request happened'
              print 'Content type ' + fileRequest.headers['content-type']
              fileContentHeader = fileRequest.headers['content-type']

              print self.filePattern + ' file found'
              saveFilename = ''
              try:
                urlSplit = thisLink.split('/')
                saveFilename = urlSplit[-1].lower()
              except:
                saveFilename = thisLink
              # saveFilename = self.fixPdfFilename(saveFilename)
              print saveFilename
              doiAsFilename = self.doi.replace('/','_')
              print doiAsFilename
              fullPath = self.__fileStoreDir + '/' + doiAsFilename + '/' +  saveFilename
              print 'saving to ' + fullPath
              if not os.path.exists(os.path.dirname(fullPath)):
                try:
                  os.makedirs(os.path.dirname(fullPath))
                except OSError as exc: # Guard against race condition
                  if exc.errno != errno.EEXIST:
                    raise
              with open(fullPath, 'wb') as fe:
                  fe.write(fileRequest.content)
                  fe.flush()
              fe.close()
              # idCounter = appendFileToGraph(doi,fullPath, idCounter)
              print 'Retrieved ' + self.filePattern  + ' file written as ' + saveFilename

              # if 'html' in fileContentHeader:
              if 'html' in thisLink or not self.filePattern in thisLink:
                print 'another html file found'
                try:
                  saveHeader(makeHeaderString(fileRequest, doi))
                  newUrl = fileRequest.url
                except:
                  pass
                # idCounter = parseForLinks(doi,fileRequest.text, linksList, baseUrl, idCounter)
                print 'calling parseForLinks with this url ' + newUrl
                self.parseForLinks(self, fileRequest.text, linksList, newUrl)
                # parseForLinks(doi,fileRequest.text, linksList, fileRequest.headers['Location'])
            except:
              print thisLink + ' request failed'
    except Exception as e: print('crossref issn ' + str(e))
