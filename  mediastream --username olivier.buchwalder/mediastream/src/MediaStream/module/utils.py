#!/usr/bin/python
# -*- coding: iso-8859-1 -*-


import os, urllib, traceback
import xbmcgui, xbmc

from elementtree.ElementTree import Element, ElementTree, parse, SubElement, ProcessingInstruction

from constants import *


class MyCancel(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    

def outPrint (message, e=None):  
    """
    Debuf fonction for printing and debugging
    """
    outstr = '\nMStream:'
    if message :
        outstr = outstr + message
        
    if LOG_VALUE == 0:
        return
    
    if LOG_VALUE >= 1:
        print outstr
    if LOG_VALUE >= 2:
        print outstr
        if e:
            traceback.print_exc()
    if LOG_VALUE >= 3:
        logfile = open(DEBUG_FILE,'a')
        logfile.write ( outstr )
        if e:
            traceback.print_exc(file=logfile)
        logfile.close() 


class myURLOpener(urllib.FancyURLopener):
    """Chris Moffitt
       Create sub-class in order to overide error 206.  This error means a
       partial file is being sent,
       which is ok in this case.  Do nothing with this error.
    """
    def http_error_206(self, url, fp, errcode, errmsg, headers, data=None):
        pass
    

def getRedirection(url):
    """
    get redirection or None when problem
    """
    myUrlclass = myURLOpener()
    webPage = myUrlclass.open(url)
    redurl = urllib.unquote_plus(webPage.geturl() )
    
    return redurl
    
## TODO: accept download of mms... 
def downloadFile(URL, filelocalPath, minSize = 50000, showDialog=True):
    """
    Download URL, display a progress window and allow resusimg and cancelation when already available.
    Modified from Chris Moffitt
    
    minSize, the minimum size, to consider as downloadable, otherwise can be streamable file, asx, ram
    -> octet, usually 50k
    
    return
    >  1 when ok fully downloaded
    >  0 when canceled, 
    > -1 when not downloadable because not streamable
    > -2 when exception during downloaded
    """
    progress1 = None
    progress = None
    try:
        progress1 = xbmcgui.DialogProgress()
        progress1.create('MediaStream','Get Information', URL)
        progress1.update(100)
        
        existSize = 0
        myUrlclass = myURLOpener()

        # if already exist get the size of the file
        if os.path.exists(filelocalPath):
            existSize = os.path.getsize(filelocalPath)
            #If the file exists, then only download the remainder
            myUrlclass.addheader("Range","bytes=%s-" % (existSize))
        
        #If the file exists, but we already have the whole thing, don't download again
        webPage = myUrlclass.open(URL)
        
        # warning when the file is fully downloaded, exception is launched
        # WARNING when the file is not downloadedable, asx, ra
        remainSize = -1
        try:
            remainSize = int(webPage.headers['Content-Length']) 
           
            if minSize > 0 and existSize == 0 and remainSize < minSize:
                # consider as a stream
                progress1.close()
                webPage.close()
                #outputFile.close()
                return -1
        except Exception, ex:
            # cannot find a length to download
            progress1.close()
            webPage.close()
            #outputFile.close()
            
            if existSize > 0:
                # the file seems to be fully downloaded, return True
                return 1                
            else:
                # the file seems to be not downloadable
                return -1
            
        progress1.close()
        
        #"File already downloaded" -> exit 
        if remainSize <= 0:
            webPage.close()
            #outputFile.close()
            return 1
        
        # File is not fully downloaded or not exising 
        
        # create here the file link
        if os.path.exists(filelocalPath):
            outputFile = open(filelocalPath,"ab")
        else:
            outputFile = open(filelocalPath,"wb")
        
        # Download or resume the url content into the file
        progress = xbmcgui.DialogProgress()
        progress.create('MediaStream','Download file', URL)
        progress.update(0)
        
        percent = 0
        # set the progress bar
        if existSize > 0:
            percent = (100 * existSize) / (remainSize + existSize)
            progress.update(percent)
            
        numBytes = 0
        while 1:
            data = webPage.read(8192) # 8kB
            if not data:
                break
            
            outputFile.write(data)
            numBytes = numBytes + len(data)
            
            percent = (100 * (existSize + numBytes)) / (remainSize + existSize)
            progress.update(percent)

            if progress.iscanceled():
                progress.close()
                webPage.close()
                outputFile.close()
                return 0
        
        progress.close()
        webPage.close()
        outputFile.close()
        return 1
    
    except Exception, ex:
        outPrint('MStream: Cannot download URL:' + URL)
        if progress1:
            progress1.close()
        if progress:
            progress.close()
        if showDialog:
            dialog2 = xbmcgui.Dialog()
            dialog2.ok('Information', 'Problem when downloading ', URL)
        return -2
    
    
def playURL( URL):
    """
    Play a media from a given URL
    """
    # bug on new xbmc
    #pls = xbmc.PlayList(1)
    #pls.clear()
    #pls.add( URL )
    monplayer = xbmc.Player()
    monplayer.play(URL)


def getLastStringPart(str, separator):
    try:
        index = str.rfind(separator, 0, len(str))
        if index < 0:
            return None
        return str[ index + 1 : len(str)]
    except :
        return None
    
def getCroppedFilename(filename, length=42):
    """
    reduce length when necessary to a limited length of characters (reduce before extension)
     """
    extension = getLastStringPart(filename, '.')
    if extension == None:
        filename = filename[0: length-1]
    else:
        if len(filename) > length:
            extLen = len(extension)
            filename = filename[0: len(filename) - (extLen + 1)]
            filename = filename[0: (length - 1) - (extLen)] + '.' + extension
    return filename
   
def getBeforeStringPart(str, separator):
    """
    reduce length until when a special char is found
     """
    try:
        index = str.rfind(separator, 0, len(str))
        if index < 0:
            return str
        return str[ 0: index ]
    except :
        return None
   

def createXmlFile(filePath, rootElement , version='1.0', encoding=ENCODING_IN ):
    """
    Create an xml file
    """
    doc = ElementTree(rootElement)
    outfile = open(filePath, 'w')    
    outfile.write('<?xml version="' + version + '" encoding="' + encoding + '" ?>')    
    doc._write(outfile, doc._root, ENCODING_IN, {})    
    outfile.close()
    
    # <?xml version="1.0" encoding="utf-8"?> !!!
    #rootPI = ProcessingInstruction("xml", 'version="1.0" encoding="utf-8"') 
    # utf-8
    #ElementTree(mediaItem).write(mediaFilePath + '.xml', encoding = ENCODING_IN)
     
      
##############################################
def createFilePodcast(mediaFilePath, title, description=''):
    """
    create the xml file using utf
    """  
    
    mediaItem = Element("media")    
    mediaItem.attrib["version"] = VERSION
    titleNode = SubElement(mediaItem, "title")
    titleNode.text = title
    descrNode = SubElement(mediaItem, "description")
    descrNode.text = description
    
    createXmlFile(mediaFilePath + '.xml', mediaItem)
    
    mediaItem.clear()



def getPodcastFileInfo(mediaFilePath):
    """
    get the podcast title, description, as a utf string
    """

    textpath = mediaFilePath + '.xml'
    file = open(textpath, "r")
    tree = parse(file)
    elemMedia = tree.getroot() # 'media'

    conf_version = elemMedia.get('version')    
    title = elemMedia.findtext('title')                    
    description = elemMedia.findtext('description', '')

    elemMedia.clear()
    file.close()

    #poditeminfo = PodcastItem()
    #poditeminfo.title = title
    #poditeminfo.description = description
    
    #return poditeminfo
    return title, description

def isStreamMediaOnly(mediaUrl):
    """
    Return if the current url is 
    """
    pass


def readFile(path, length=10000000):
    """
    max 10mo
    """
    file = open(path,"r")
    data = file.read(length)
    file.close()
    
    return data


   
#############################################################################################
def createDirectory(dirpath, dialogON=True, recursive=True):
    """
    return true if create or exist, and False if an error occurs 
    """
    
    try:
        if os.path.exists(dirpath) == False:
            if recursive:
                os.makedirs(dirpath)
            else:
                os.mkdir(dirpath)
        return True
    except:
        if dialogON:
            dialog2 = xbmcgui.Dialog()
            dialog2.ok('Warning', 'Cannot create directory', dirpath)        
        return False
    

def cleanString(str):
    """
    Return a cleaned string without all special characters.. ':', '-'
    """
    return str.replace('/','_').replace("\000","_").replace("\\","_").replace(":","_").replace("*","_").replace("?","_").replace("\"","_").replace("<","_").replace(">","_").replace("|","_").replace("\'","_").replace("-","_").replace("!","_").replace("&","_").replace("%","_").replace("/","_").replace("+","_").replace(",","_").replace(";","_").replace("=","_").replace("(","_").replace(")","_").replace("\`","_").replace("\^","_")

