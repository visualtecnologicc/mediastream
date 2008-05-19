#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os, urllib, fnmatch, time, datetime

from elementtree.ElementTree import Element, ElementTree, parse, XML
from datetime import date, timedelta

from constants import *
from utils import *



#############################################################################################
class Channel:
    def __init__(self, name, baseURL, imagelink, description, options, categoryId, catChanList):
        ####################
        self.programs = []
        self.optionsSelectedValue=[]  # selected values 
                
        ####################
        #init defautl optional value
        self.name         = 'Undefined'
        self.baseURL      = ''
        self.imagelink    = DEF_CHANNEL_PIC  # !! IMAGES + DEF_CHANNEL_PIC
        self.description  = ''
        self.options      = []               # a list of option dico: descr, values, labels
        self.categoryId   = None 
        self.catChanList  = []
        ####################
        if name:
            self.name = name
        if baseURL:
            self.baseURL = baseURL
        if imagelink:
            # test image before assigning
            if os.path.exists(IMAGES + imagelink):            
                self.imagelink = imagelink
            else:
                # use default
                pass
        if description:
            self.description = description
        if options and len(options) > 0:
            self.options = options
            
        if categoryId:
            self.categoryId = categoryId
        if catChanList:
            self.catChanList = catChanList


    def addProgram(self, program):
        self.programs.append(program)
        program.channel = self

#############################################################################################
class Program:
    def __init__(self, name, description, URLPattern, podcast, imagelink, prooptions, diffusionInfo, avail, categoryId, filemode = None):
        ####################               
        self.channel = None
        self.prooptionsSelectedValue = [] # selected values 
        
        ####################               
        #init defautl optional value
        self.name          = 'Undefined'
        self.description   = ''
        self.diffusionInfo = []
        self.prooptions    = []
        self.imagelink     = DEF_PROGRAM_PIC  # IMAGES + 
        self.avail         = None
        self.URLPattern    = None
        self.podcast       = None # when a podcast is defined, override other properties
        self.categoryId    = None
        self.filemode      = None # when podcast, the download name is processed using the title when = "title"
        ####################
        if name:
            self.name = name
        if description:
            self.description = description
        if imagelink:
            # test image before assigning
            if os.path.exists(IMAGES + imagelink):            
                self.imagelink = imagelink
            else:
                # use default
                pass
        if URLPattern:
            self.URLPattern = URLPattern
        if podcast:
            self.podcast = podcast
        if prooptions and len(prooptions) > 0:
            self.prooptions = prooptions
        if diffusionInfo:
            self.diffusionInfo = diffusionInfo
        if avail:
            self.avail = avail
        if categoryId:
            self.categoryId = categoryId
        if filemode:
            self.filemode = filemode
  
             
    # -------------------------------------------------------------------------------------------
    def getDiffusionDates(self):
        if self.diffusionInfo == None:
            return None
        
        diffs = []
        #from datetime import date
        now = date.today()
                    
        #now returns last 5 days
        for i in range(0, 2000) :
            deltaDayDate = timedelta(days=i)
            
            # choose a past day
            aday = now - deltaDayDate
            
            # 0= monday, 6=sunday
            weekdayIdx = aday.weekday()
            
            for diffiStr in self.diffusionInfo:
                diffidx = int(diffiStr)
            
                #live:-1 -> return empty
                if diffidx == -1:
                    return []
                #quotidien: 7 -> add all days
                if diffidx == 7:
                    #diffs.append(aday)
                    if self.appendDay(aday, diffs, i) == False: 
                        break
                #hebdo: 0-6
                elif diffidx >= 0 and diffidx <= 6 :
                    if weekdayIdx == diffidx:
                        #diffs.append(aday)
                        if  self.appendDay(aday, diffs, i) == False: 
                            break
                #qot wo we: 8
                elif diffidx == 8 :
                    if weekdayIdx >= 0 and weekdayIdx <= 4:
                        #diffs.append(aday)
                        if  self.appendDay(aday, diffs, i) == False: 
                            break
                #sa+di: 9
                elif diffidx == 9 :
                    if weekdayIdx == 5 or weekdayIdx == 6:
                        #diffs.append(aday)
                        if  self.appendDay(aday, diffs, i) == False: 
                            break
                
        return diffs

    # -------------------------------------------------------------------------------------------
    def appendDay(self, aday, diffusionList, deltaDayInt):
        """
        Add a new day to the given list and return true, when the avail parameter doesn't allow it return false
        
        # e.g. : avail : {'start' : '11/01/04'} || {'nbdays' : '20'}  || {'nbdiff' : '5'} 
        
        TODO don't convert from string, use directly the numeric types
        """
        if self.avail == None:
            diffusionList.append(aday)
            return True
        else:
            
            # test that current date is not older than limit 
            if self.avail.has_key('start'):
                # convert the str date to date object
                startDate = datetime.date.fromtimestamp(time.mktime(time.strptime(self.avail['start'], "%d/%m/%Y")))
                if aday >= startDate:
                    diffusionList.append(aday)
                    return True
                else:
                    return False
                
            # test that the current date is not bigger than the limit 
            elif self.avail.has_key('nbdays'):
                nbdaysLimit = self.avail['nbdays']
                nbdaysIntLimit = int(nbdaysLimit)
                if deltaDayInt <= nbdaysIntLimit:
                    diffusionList.append(aday)
                    return True
                else:
                    return False
         
            # test that the number of diffusion element is lower than the limit   
            elif self.avail.has_key('nbdiff'):
                nbdiffuLimit = self.avail['nbdiff']
                nbdiffuIntLimit = int(nbdiffuLimit)
                if len(diffusionList) <=  nbdiffuIntLimit:
                    diffusionList.append(aday)
                    return True
                else:
                    return False
                
            else:
                # add this date
                diffusionList.append(aday)
                return True
        
        
    # -------------------------------------------------------------------------------------------
    def getFullURL(self, URL, aDate):    
        """
            Return the full URL to play, with option and dates replaced in the URL
        """
        
        if URL == None:
            return None
        
        fullURL = URL
        try:            
            # replace the main url        
            if self.channel.baseURL:
                fullURL = fullURL.replace('$URL', self.channel.baseURL)
            
            # test if selected option list valid, and iterate each option
            if self.channel.optionsSelectedValue and len(self.channel.optionsSelectedValue) > 0 :
                i = 1
                for sel_option_i in self.channel.optionsSelectedValue:
                    if sel_option_i != None:
                        fullURL = fullURL.replace('$CH_OPTION'+ str(i), sel_option_i)
                    else:
                        outPrint('Cannot access to the selected option value'  + i + ', for channel '+ self.channel.name)
                    i = i+1

            # test if selected prooption list valid, and iterate each prooption
            if self.prooptionsSelectedValue and len(self.prooptionsSelectedValue) > 0 :
                i = 1
                for sel_prooption_i in self.prooptionsSelectedValue:
                    if sel_prooption_i != None:
                        fullURL = fullURL.replace('$PR_OPTION'+ str(i), sel_prooption_i)
                    else:
                        outPrint('Cannot access to the selected option value ' + i + ', for program '+ self.name)
                    i = i+1
                
            # when the url was in an option, try to replace the main url another time  
            if self.channel.baseURL:
                fullURL = fullURL.replace('$URL', self.channel.baseURL)
                        
            # address the date
            if aDate:
                fullURL = fullURL.replace('$DAY', aDate.strftime('%d'))
                fullURL = fullURL.replace('$MONTH', aDate.strftime('%m'))
                fullURL = fullURL.replace('$YEAR2', aDate.strftime('%y'))
                fullURL = fullURL.replace('$YEAR4', aDate.strftime('%Y'))
                fullURL = fullURL.replace('$YEAR', aDate.strftime('%Y'))
            
            return fullURL

        except Exception, ex:
            outPrint('Problem when processing URL:'  + fullURL, ex)
            return None

#############################################################################################
class Category:
    def __init__(self, name, id, parentid, imagelink ):

        ####################
        #init defautl optional value
        self.name         = 'Undefined'
        self.id           = 'Undefined'
        self.imagelink    = DEF_CHANNEL_PIC
        self.parentid     = None

        ####################
        if name:
            self.name = name
        if id:
            self.id = id
        if imagelink:
            # test image before assigning
            if os.path.exists(IMAGES + imagelink):            
                self.imagelink = imagelink
            else:
                # use default
                pass
        if parentid:
            self.parentid = parentid


#############################################################################################
class PodcastInfo:
    """
    Main information
                TODO make it valis also with other non-podcast media, to be able to downlaod them...
    """
    def __init__(self):
        
        # constant parameters
        self.title = ''
        self.description = None
        self.image = None
    
        #dynamic
        self.contentXML = None
        self.targetDirectory = None
        self.titleAscii = ''
        
        # list of all podcast items
        self.itemsInfo =[]

        # the title list to display
        self.titles2display =[]
        
        # the file name list, used to check that the files are downloaded or not
        self.itemFilenames =[]
        
        # the local node reference to the file report node
        self.localElementRoot = None
        
        # TODO
        self.useTitleForName = False
        
#############################################################################################
#############################################################################################


#############################################################################################
class PodcastItem:
    """
    Element information
    """
    def __init__(self):
        
        # constant properties
        
        self.description = ''
        self.size = 0
        self.length = 0
        self.type = None
        self.pubdate = None
        self.duration = None
                
        # is set to true when fully downloaded 
        self.flagfinish = False

        
        # dynamic parameters
        self.title = ''
        self.url = None  # '' -> local only
        
        self.filename = None
        self.fileLocation = None
        
        # true when the file is local
        self.isLocal = False




#############################################################################################
def readMediaElementTree(filePath, encoding = ENCODING_IN):
    """
    Open the media file and return the list of all channels with programs
    and the version
    """

    file = open(filePath, "r")
    tree = parse(file)
    elemMedia = tree.getroot()
    
    channelsList = []
    catList = []
    achannel = None
    
    conf_version = elemMedia.get('version')
    conf_author  = elemMedia.get('author')
    conf_date    = elemMedia.get('date') 
    
    #for error printing
    channame = None
    progname = None
    ####################
    

    # read main category
    for elemCategory in elemMedia.getiterator('category'):
        try:
            name= elemCategory.text
            id = elemCategory.get('id')
            imagelink = elemCategory.get('imagelink')
            parentid = elemCategory.get('parentid')
            
            acat = Category(name, id, parentid, imagelink)
            catList.append(acat)
        except Exception, ex:
            nn = name
            if nn == None:
                nn=''
            outPrint('problem when reading category ' + nn, ex)
        elemCategory.clear()
        
            
    for elemChannel in elemMedia.getiterator('channel'):
        try:
            nameElem = elemChannel.find('name')            
            channame = nameElem.text.encode(encoding, 'replace')
            nameElem.clear()
            
            baseurl = elemChannel.get('baseurl')
            imagelink = elemChannel.get('imagelink')
            
            categoryId =  elemChannel.get('category')
            
            description = ''
            descriptionElem= elemChannel.find('description')
            if descriptionElem != None:
                description = descriptionElem.text.encode(encoding, 'replace')
                descriptionElem.clear()
            
            ####################
            options=[]
            for elemOption in elemChannel.getiterator('option'):
                option_item_desc = ''
                option_item_values = []
                option_item_labels = []
    
                option_desc = elemOption.find('descr')
                if option_desc != None:
                    option_item_desc = option_desc.text.encode(encoding, 'replace')
                    option_desc.clear()
                                                    
                for elemItem in elemOption.getiterator('item'):
                    option_value = elemItem.get('value')
                    option_item_values.append(option_value)                

                    if elemItem.text != None:
                        option_item_labels.append(elemItem.text.encode(encoding, 'replace'))
                    
                    elemItem.clear()
                    
                ##a list of option dico: descr, values, labels
                options.append({'descr' : option_item_desc, 'values': option_item_values, 'labels':option_item_labels })
            
                elemOption.clear()
            
            ##########
            #### -> CHANNEL
            catChanList = [] #not implemented yet
            
            achannel = Channel(channame, baseurl, imagelink, description, options, categoryId, catChanList)
            channelsList.append(achannel)
            
            
            ####################
            for elemProgram in elemChannel.getiterator('program'):
                try:
                    nameElem = elemProgram.find('name')
                    progname=nameElem.text.encode(encoding, 'replace')
                    nameElem.clear()
                    
                    url = elemProgram.get( 'url')
                    
                    # TODO improve this...
                    ispodcast = elemProgram.get('ispodcast')                    
                    podcast = None
                    if ispodcast and (ispodcast.lower() == "true" ):
                        podcast = url
                        url = None
                    
                    filemode = elemProgram.get('filemode')     
                    
                    imagelink= elemProgram.get('imagelink') 
                    
                    description = ''
                    descriptionElem= elemProgram.find('description')
                    if descriptionElem != None:
                        description = descriptionElem.text.encode(encoding, 'replace')
                        descriptionElem.clear()
                        
                    ###
                    diffusionInfo = []
                    for diffNode in elemProgram.getiterator('diffusion'):                        
                        diffid = diffNode.get('id')
                        diffusionInfo.append(diffid);
                        diffNode.clear()
        
                    ### 
                    options = []
                    for optionNode in elemProgram.getiterator('prooption'):
                        option_item_desc = ''
                        option_item_values = []
                        option_item_labels = []
                    
                        option_desc = optionNode.find('descr')

                        if option_desc != None:
                            option_item_desc = option_desc.text.encode(encoding, 'replace')
                            option_desc.clear()
                                                            
                        for elemItem in optionNode.getiterator('item'):
                            option_value = elemItem.get('value')
                            option_item_values.append(option_value)                
        
                            if elemItem.text != None:
                                option_item_labels.append(elemItem.text.encode(encoding, 'replace'))
                            elemItem.clear()
                            
                        options.append({'descr' : option_item_desc, 'values': option_item_values, 'labels':option_item_labels })
                        optionNode.clear()
        
                    ### only 1 expected
                    avail = None
                    availNode = elemProgram.find('avail')
                    if availNode != None:
                        type = availNode.get('type')
                        value = availNode.get('value')
                        avail = {type : value}
                        availNode.clear()
                        # only 1
                        #break; 
                      
                    #####
                    ## -> PRogram
                    #
                    categoryId = None #not implemented yet
                    aprogram = Program(progname, description, url, podcast, imagelink, options, diffusionInfo, avail, categoryId, filemode)
                    achannel.addProgram(aprogram)
                    elemProgram.clear()
                    
                except Exception, ex:
                    nn = progname
                    if progname == None :
                        nn = ''
                    outPrint('read media config: error during program processing, ignored:' + nn, ex)
                    continue  
                 
            elemChannel.clear()  
                 
        except Exception, ex:
            nn = channame
            if channame == None :
                nn = ''
            outPrint('read media config: error during channel processing, ignored:' + nn, ex)
            achannel = None
            continue
        
    elemMedia.clear()
#    tree.close()
    file.close()   
    return channelsList, catList, conf_version


#############################################################################################
def processRmFile(rmURL):
    """
    Get the real media file (rm,ram,rmvb) and returns the real redirected url.
    When not a rm file return the given link.
    """
    
    urlToPlay = rmURL
    
    if rmURL and (rmURL.endswith('.rm') or rmURL.endswith('.ram') or rmURL.endswith('.rmvb')) :
        #read the redirected link for real especially
        urlredirect = urllib.urlopen(rmURL).read()
        # redirect possible try to search if rm
        idx = urlredirect.find('?')
        if idx :
            urlToPlay = urlredirect[:idx]
        else:
            urlToPlay = urlredirect                 
    
    return urlToPlay


#############################################################################################
def getDiffusionDate(program):
    """
    return None when no date
    """    
    selectDate = None
    # Ask for the diffusion dates when defined
    diffDates = program.getDiffusionDates()
    if diffDates and len(diffDates) > 0:
        diffsStrs = []                    
        # fill the date string
        for date in diffDates:
            diffsStrs.append(date.strftime('%d/%m/%Y'))

        dialog = xbmcgui.Dialog()
        dateIdx = dialog.select("Select a Date", diffsStrs) 
        if dateIdx >= 0 and dateIdx < len(diffDates):
            toPlay = True
            selectDate = diffDates[dateIdx]
        else:
            raise MyCancel('Exit')
   
    return selectDate
            
    
#############################################################################################
def chooseOptions(optionsList):
    """
    Present a list, when error -> exceptions
    selectedvalues is the out selection 
    
    cancel -> raise NameError('Exit')
    
    return selectedvalues
    """
    
    selectedvalues = []
    canceled = False

    try:
        # Ask for the options indexwhen defined, open a dialog by option
        if optionsList and len(optionsList) > 0:
            
            #init the selected list with None
            for option_i in optionsList:
                selectedvalues.append('')    # TODO replace by None
    
            i=0
            for option_i in optionsList:
                # Get the option description
                descr = ''
                listLabels = None
                values = None
                if option_i.has_key('descr'):
                    descr = option_i['descr']
                #optional
                if option_i.has_key('labels'):
                    labels = option_i['labels']
                    listLabels = labels
                
                # mandatory
                values = option_i['values']
                
                # test if labels valid, otherwise get values for display
                if listLabels == None or (values != None and len(listLabels) != len(values)):
                    listLabels = values
                
                if values == None or len(values) < 1:
                    outPrint('problem when accessing to options values list: '+ optionsList, ex)
                    raise Exception
                else:
                    dialog = xbmcgui.Dialog()
                    optionIdx = dialog.select("Select the Option: " + descr , listLabels) 
                    if optionIdx >= 0 and optionIdx < len(values):
                        # Write the Selected value
                        selectedvalues[i] = values[optionIdx]
                    else:
                        #canceled 
                        canceled = True
                        break
                        #raise NameError('Exit')
                
                # increase counter
                i = i+1

    except Exception, ex:
        outPrint('problem when accessing to options list: '+ optionsList, ex)
        raise
    
    if canceled == True:
        raise MyCancel('Exit')

    return selectedvalues


#############################################################################################
def retriveURLContent(url):
    """
    access  to a url and return the content string and display a dialog,
    when a problem occur, raise exception
    """
    dialog = None
    socket = None
    
    try:
        dialog = xbmcgui.DialogProgress()
        dialog.create('MediaStream', 'Get Information', url)
        
        # Access to URL XML file
        socket = urllib.urlopen(url)
        content = socket.read()            
        socket.close()
        dialog.close()
    except:
        if dialog != None:
            dialog.close()
        if socket != None:
            socket.close()
        raise
    
    return content
    

#############################################################################################

def parsePodcast(podcastXML, config, filemode=None):
    """
    Access to the podcast and return all information in a podcast object
    
    return None when no info available, when error raise MyCancel
    """
    podcastInfo = PodcastInfo()                    
    podcastNode = XML(podcastXML)
    channelNode = podcastNode.find('channel')
    
    ### TODO handle when title is empty, use the program title
    titlePodcast = channelNode.findtext('title', '')
    titlePodcastAscii = titlePodcast.encode('ascii', 'ignore')

    if not titlePodcast:
        titlePodcast = 'UNDEFINED'
        titlePodcastAscii = 'UNDEFINED'
    else:
        titlePodcastAscii = getCroppedFilename(titlePodcastAscii)
        titlePodcastAscii = cleanString(titlePodcastAscii)
    
    ## TODO support the podcast named the same way... add a hashcode after the title, and a main podcast.xml file at the root
    
    # the target local directory
    targetDirectory = config.podcastDownloadPath + titlePodcastAscii
    chandescription   = channelNode.findtext('description', '')
    #chanImage         = getXMLAttrText(channeldom, 'itunes:image', 'href')

    ####
    podcastInfo.title = titlePodcast
    podcastInfo.description = chandescription
    #podcastInfo.image = chanImage    
    podcastInfo.titleAscii = titlePodcastAscii
    podcastInfo.targetDirectory = targetDirectory    
    
    # Get the local info, and a link on the elemnt node, to be modified later
    podcastLocalInfo = getPodcastLocalItems(podcastInfo)
    
    # parse the item list
    #items = channeldom.getElementsByTagName('item') 
    itemExist = channelNode.find('item') != None
                        
    if not itemExist:
        # return empty mark
        return None
    
    #for item in items:
    for itemNode in channelNode.getiterator('item'):
        descr = ''
        type = ''
        length = ''
        
        title = itemNode.findtext('title', '')
        descr      = itemNode.findtext('description', '')                                      
        #pubDate    = getXMLTagText(item, 'pubDate')
        #duration   = getXMLTagText(item, 'itunes:duration')     

        enclosureNode = itemNode.find('enclosure')
        if enclosureNode == None:
            continue
        
        # the url can be redirect, urllib follow this link for downlaod                             
        url = enclosureNode.get('url')
        if url == None:
            # when no url, continue
            continue 
        
        # search in the local if the file is already here, already downloaded, and add it
        foundLocalItem = None        
        for podlocalitem in podcastLocalInfo.itemsInfo:
            if podlocalitem.url == url:
                foundLocalItem = podlocalitem
        if foundLocalItem != None:            
            podcastInfo.itemsInfo.append(foundLocalItem)    
            continue
        
        # type is not always defined?!, can test with urllib when downloaded
        type       = enclosureNode.get('type')
        # Length only used for information as list, exact size is found later during download
        length       = enclosureNode.get('length')
                                                                
        #####################
        podItem = PodcastItem()
        podItem.title = title
        podItem.description = descr
        podItem.url = url
        podItem.type = type
        podItem.length = length
        podcastInfo.itemsInfo.append(podItem)    


    # TODO ?? return when ! config.podcastDownload

    # init the titles and the filename, filelocation
    for podItem in podcastInfo.itemsInfo :
        
        # the display title 
        title = podItem.title
        
        # when is local, don't process filenames and add >> in the titles
        if podItem.isLocal:
            # control that the file exist and fully downloaded, when not try to download ...
            if not os.path.exists(podItem.fileLocation) : 
                podItem.isLocal = False
                podItem.flagfinish = False
                
            elif podItem.flagfinish:
                title = '>> ' + title                  
            else: 
                title = '<> ' + title              
        
        # when not local, or not file found
        else :
            
            # TODO test that valid name, no special char, len > sufficient, and not always the same name, 
            # TODO OR add something in the MEDIA xml file
            
            ## TODO when a podcast title is many time the same, use a hascode after the title filaname

            
            ### PROBELM avec la limite des path: lorsque fichier trop long, peut avec des equivalent......
            
            #  podcastInfo.useTitleForName or
            if  filemode == "title":
                filename = podItem.title
                podcastInfo.useTitleForName
            else:
                filename = getLastStringPart(podItem.url.encode('ascii', 'ignore'), '/')    
                filename = getBeforeStringPart(filename, '?')
                
                ### TODO test if this filename already exit in the list..?? -> if YES MARK it using a poditem flag, and use title...
                
                
            filename = getCroppedFilename(filename) # 42-4   
            filename = cleanString(filename)
            
            fileLocation = targetDirectory + '\\' + filename
            
            # set the properties
            podItem.filename = filename
            podItem.fileLocation = fileLocation
            
            # When the file exist but no entry in the xml add it here 
            if os.path.exists(podItem.fileLocation) : 
                title = '>? ' + title   
            
        # process size
        size = 0
        if podItem.size != 0 :
            size = podItem.size
        elif podItem.length and len(podItem.length) > 0:
            size = round(long(podItem.length) / 1000000.0 , 1)     
        # set size and title
        if size != 0:
            podItem.size = size
            title = title + ' (' + str(size) + 'Mo)'
        
        podcastInfo.itemFilenames.append(podItem.filename)
        podcastInfo.titles2display.append(title)
    
    
    # search in the folder if already downloaded file are available, and not refferenced in the xml
    appendLocalMedia(podcastInfo, podcastLocalInfo)
    
    # return the podcast info with items
    return podcastInfo
    


#############################################################################################
def appendLocalMedia(podcastInfo, podcastLocalInfo) :
    """
    This method search in the podcast download directory for already downloaded files that are not defined in the current podcast file
    
    - if the media directory or file exist, return without errors
    """
    
    targetDirectory = podcastInfo.targetDirectory
    podItems = podcastInfo.itemsInfo
    
   
    # search in the folder if already downloaded file are available, and not refferenced in the xml
    if  os.path.exists(targetDirectory) and os.path.isdir ( targetDirectory ):
        for itemLocal in podcastLocalInfo.itemsInfo:
           try:
               # TODO control that podcastInfo.itemFilenames when already exist ... no automatic name !!!
               if podcastInfo.itemFilenames.__contains__(itemLocal.filename):
                   continue
                   
               localFileLocation = targetDirectory + '\\' + itemLocal.filename
               if os.path.exists(localFileLocation) == False :
                   ## ??????? remove it ?
                   continue
               
               # add the local element to the downloaded element
               podcastInfo.itemsInfo.append(itemLocal)
               podcastInfo.itemFilenames.append(itemLocal.filename)
               podcastInfo.titles2display.append('<< ' + itemLocal.title)

       ###
       ## TODO pehaps add the file that are not in the xml...
       
           except Exception, ex:
               outPrint('problem when accessing to already downloaded podcasts', ex)
               

#############################################################################################
def getPodcastLocalItems(podcastInfo):
    """
    search in the media dir if the podcast dir already exist, read it, return a reference on the tree!, 
    
    return podcastLocalInfo that include the element root, warning not cleared
    
    """
    
    podcastLocalInfo = PodcastInfo()
    reportList = []
    reportFilename = podcastInfo.targetDirectory + '\\_podcast.xml'
    elemMedia = None
    
    # try to create dir
    #if not createDirectory(podcastInfo.targetDirectory):
    #    raise MyCancel('Exit')
    
    if os.path.exists(reportFilename):
        # real all pathes
        
        file = open(reportFilename, "r")
        tree = parse(file)
        elemMedia = tree.getroot() # 'media'
    
        # get the global info here... maintitle, main description ??? YES
        conf_version = elemMedia.get('version')    
        maintitle = elemMedia.findtext('title', '')                    
        maindescription = elemMedia.findtext('description', '')
        podcastLocalInfo.title = maintitle
        podcastLocalInfo.description = maindescription
    
        for itemNode in elemMedia.getiterator('item'):
            url = itemNode.get('url')
            filename = itemNode.get('filename')
            flagfinish = itemNode.get('isfinished')
            
            title = itemNode.findtext('title', '')                    
            description = itemNode.findtext('description', '')
        
            itemReport = PodcastItem()
            itemReport.url = url
            itemReport.filename = filename
            # init location
            fileLocation = podcastInfo.targetDirectory + '\\' + filename
            itemReport.fileLocation = fileLocation
            itemReport.isLocal = True
            itemReport.flagfinish = flagfinish != None and flagfinish.lower() == 'true'
            itemReport.title = title
            itemReport.description = description
            
            podcastLocalInfo.itemFilenames.append(filename)
            podcastLocalInfo.itemsInfo.append(itemReport)
        
        #elemMedia.clear()
        file.close()
        
        
    else:
        #init the main info
        podcastLocalInfo.title = podcastInfo.title
        podcastLocalInfo.description = podcastInfo.description
                
        elemMedia = Element("media")
        elemMedia.attrib["version"] = VERSION
        
        titleNode = SubElement(elemMedia, "title")
        titleNode.text = podcastLocalInfo.title
        descrNode = SubElement(elemMedia, "description")
        descrNode.text = podcastLocalInfo.description
    
    # add it to the both elements
    podcastInfo.localElementRoot = elemMedia
    
    return podcastLocalInfo



def appendItem2Local(podcastInfo, podcastItem, isfinished=True):
    """
    add the podcast item into the media element...
    """
    
    elementRoot = podcastInfo.localElementRoot
    reportFilename = podcastInfo.targetDirectory + '\\_podcast.xml'
    finishstr = "false"
    if isfinished:
        finishstr = "true"
            
    # search for the element with the url
    for itemNode in elementRoot.getiterator('item'):
        url = itemNode.get('url')
        
        if url != podcastItem.url:
            continue
        # when url is found set the flag set the flag when differetn
        

        itemNode.attrib["isfinished"] = finishstr
        
        #filename = itemNode.get('filename')
        #flagfinish = itemNode.get('isfinished')
        
        #title = itemNode.findtext('title', '')                    
        #description = itemNode.findtext('description', '')
        
        createXmlFile(reportFilename, elementRoot)
        return 
    
    # not found create a new entry for the given item
    itemNode = SubElement(elementRoot, "item")
    itemNode.attrib["url"] = podcastItem.url
    itemNode.attrib["filename"] = podcastItem.filename
    itemNode.attrib["isfinished"] = finishstr #podcastItem.flagfinished
    
    titleNode = SubElement(itemNode, "title")
    titleNode.text = podcastItem.title
    descrNode = SubElement(itemNode, "description")
    descrNode.text = podcastItem.description
    
    createXmlFile(reportFilename, elementRoot)
    
    
#############################################################################################
class UserConfig:
    """
    TODO make media conf loadable using web    
    must be saved in the config dir, not in the script mediastream folder
    """
    
    def __init__(self, podcastDownloadPath, podcastDownload, mediaUpdateURL, logvalue ):

        ####################
        #init defautl optional value
        self.podcastDownloadPath    = MEDIA_PODCAST_DIR
        self.podcastDownload        = PODCAST_DOWNLOAD
        self.logvalue               = LOG_VALUE
        self.mediaUpdateURL         = MEDIA_UPDATE_URL

        ####################
        if podcastDownloadPath:
            self.podcastDownloadPath = podcastDownloadPath
        if podcastDownload:
            self.podcastDownload = podcastDownload
        if logvalue:
            self.logvalue = logvalue
        if mediaUpdateURL:
            self.mediaUpdateURL = mediaUpdateURL


def readScriptConfig():
    """
    Read the config from the config directory, when not already exist init the default path
    test the F drive
    """
    config = None
    
    ### faire un bouton update from internet ... copy..  
    if os.path.exists(CONFIG_FULL_PATH):
        # parse config
        file = open(CONFIG_FULL_PATH, "r")
        
        tree = parse(file)
        elemConfig = tree.getroot() # 'config'
        
        logvalue = elemConfig.findtext('logvalue')
        intLogValue = 0
        # Set the global log value LOG_VALUE
        if logvalue != None:
            intLogValue = int(intLogValue)
            LOG_VALUE = intLogValue
        
        mediaNode = elemConfig.find('media')
        mediaUpdateURL = mediaNode.get('updateurl')
        
        podcastNode = elemConfig.find('podcast')
        podcastDownload = podcastNode.get('download')
        
        ispodcastDownload = PODCAST_DOWNLOAD
        if podcastDownload != None:
            ispodcastDownload = podcastDownload.lower() == "true"
        
        podcastDownloadPath = podcastNode.get('localpath')

        # init the config
        config = UserConfig(podcastDownloadPath, ispodcastDownload, mediaUpdateURL, intLogValue)
    else:
        #create the default config 
        config  = UserConfig(None,None,None,None)
        # save it
        saveScriptConfig(config)

    # Test the media location path, use alternative otherwise     
    if os.path.exists(config.podcastDownloadPath) == False:
        retc = createDirectory(config.podcastDownloadPath, False)
        if retc == False:
            #dialog2 = xbmcgui.Dialog()
            #dialog2.ok('Warning','Cannot Access to:' , config.podcastDownloadPath, 'Will use: ' + MEDIA_PODCAST_DIR_ALT)      
            
            config.podcastDownloadPath = MEDIA_PODCAST_DIR_ALT
            saveScriptConfig(config)

            if not os.path.exists(config.podcastDownloadPath):
                retc = createDirectory(config.podcastDownloadPath, False)
                if retc == False: 
                    dialog2 = xbmcgui.Dialog()
                    dialog2.ok('Warning', 'Cannot Access to:', MEDIA_PODCAST_DIR_ALT, 'Will not be able to download podcasts.')      

    return config
    

def saveScriptConfig(config):
    """
    save it into the the config 
    """
    
    elemConfig = Element("config")

    lognode = Element("logvalue")
    elemConfig.append(lognode)
    lognode.text = str(config.logvalue)
    
    mediaNode = Element("media")
    mediaNode.attrib["updateurl"] = config.mediaUpdateURL
    elemConfig.append(mediaNode)
    
    podcastNode = Element("podcast")
    podcastNode.attrib["download"] = str(config.podcastDownload)
    podcastNode.attrib["localpath"] = config.podcastDownloadPath
    elemConfig.append(podcastNode)
    
    # create the userdata dir when not exist
    if not os.path.exists(CONFIG_DIR):
        createDirectory(CONFIG_DIR_ROOT, recursive=False)
        createDirectory(CONFIG_DIR, recursive=False)
    
    if os.path.exists(CONFIG_DIR):
        createXmlFile(CONFIG_FULL_PATH, elemConfig, encoding='ascii')
    else:
        outPrint('Cannot create the user config file: '+ CONFIG_FULL_PATH)

