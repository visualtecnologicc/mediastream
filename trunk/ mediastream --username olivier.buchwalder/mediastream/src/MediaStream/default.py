#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

"""
    Media Stream, A script for streaming / downloading audio, videos and podcasts
    
        oli@euromobile.ch  < http://gueux-forum.net/index.php?showtopic=146820  >

    << Thanks to alexsolex, Temhil, nuka1195 for help or contributions >>

    TODO:
    - fix continue download, or debug.log file on MacOSX
    - add urlopen before playing, test redirect, test content type, test RESPOND,  and remove always parameters after '?' ??
    - add support divers site web with regex parsing, sub menus.
    - add: the podcast must be presented in a specific window, with image and description, support all type of podcast, not only with media audio and videos
    - add multi download in external thread, with a window that presents all download state
    - add support be able to download also the non-podcast
	- add test dead links, before playing?
    - add support badly named podcast for downloading
    - add support window XML skins
    - add list of categories (id transformed to list of ids)
"""


import xbmcgui, xbmc
import os, gc, sys, shutil, re

from module.constants import *
from module.utils import *
from module.main import *


#----------------------------------------------------------------------------
class ChannelWindow(xbmcgui.Window): 
    def __init__(self,rootwin=None):
        try:
            self.rootwin = rootwin
            channel = rootwin.channel
            self.channel = channel
            self.programs = channel.programs
            
            # init scale values
            self.scaleX = ( float(self.getWidth())  / float(SIZE_WIDTH) )
            self.scaleY = ( float(self.getHeight()) / float(SIZE_HEIGHT) )
            
            # add the background
            self.addControl(xbmcgui.ControlImage(0, 0, self.getScX(SIZE_WIDTH), self.getScY(SIZE_HEIGHT), BACKGROUND2))
            # add the channel image element
            self.addControl(xbmcgui.ControlImage(self.getScX(90), self.getScY(60), self.getScX(90), self.getScY(60), os.path.join(IMAGES,channel.imagelink)))
            # add the label of the channel
            self.strActionInfo = xbmcgui.ControlLabel(self.getScX(220), self.getScY(70), self.getScX(500), self.getScY(30), "", "font14", "0xDDDDDDFF") 
            self.addControl(self.strActionInfo) 
            if channel.description:
                self.strActionInfo.setLabel(channel.name + " :  " + channel.description) 
            else:
                self.strActionInfo.setLabel(channel.name ) 
                         
            # add the list of programs    
            self.list = xbmcgui.ControlList(self.getScX(83), self.getScY(140), self.getScX(548), self.getScY(400),
                                        buttonTexture=LIST_SELECT_BG,
                                        buttonFocusTexture=LIST_SELECT_BG_FOCUS,
                                        textColor='0xFFFFFFFF',
                                        itemHeight=self.getScY(50),
                                        space=2,
                                        itemTextXOffset=self.getScX(20),
                                        imageWidth=self.getScX(150),
                                        imageHeight=self.getScY(28))
            self.addControl(self.list)
        
            # add the programs into the list 
            for program in channel.programs:
                self.list.addItem(xbmcgui.ListItem(program.name + ' ' + program.description, thumbnailImage=os.path.join(IMAGES,program.imagelink)))
            self.setFocus(self.list)
        
        except Exception, ex:
            outPrint('Unable to init the program list', ex)
            self.close()


    # -------------------------------------------------------------------------------------------
    def getScY(self, y):
        return int(y * self.scaleY)

    def getScX(self, x):
        return int(x * self.scaleX)

    # -------------------------------------------------------------------------------------------
    def onAction(self, action): 
        if action == ACTION_PREVIOUS_MENU or action == ACTION_B: 
            self.close() 

        elif action == ACTION_Y or action == ACTION_INFO:
            win = PrefsWindow(config=self.rootwin.mainConfig, mVersion=self.rootwin.mediaVersion)         
            win.doModal() 
            del win 
        
        #if self.getFocus()  == self.list and (action == ACTION_MOVE_RIGHT or action == ACTION_MOVE_LEFT):
        #    self.setFocus(self.checkDownloadPodcast)
            
        #elif self.getFocus()  == self.checkDownloadPodcast and (action == ACTION_MOVE_RIGHT or action == ACTION_MOVE_LEFT or action == ACTION_MOVE_DOWN or action == ACTION_MOVE_UP):
        #    self.setFocus(self.list)
            
    # -------------------------------------------------------------------------------------------
    def onControl(self, control):
        try:
            
            if control == self.list:
                program =  self.programs[self.list.getSelectedPosition()]
                self.program = program
                
                # The URL of the emission  
                urlemission = None                        
                # Choose prooption
                program.prooptionsSelectedValue = chooseOptions(program.prooptions)
                # the config
                config = self.rootwin.mainConfig                
                
                # Podcast processing , no date to choose, but read the xml links, and proposes the links
                if self.program.podcast:
                    # get the url with modification option
                    urlemission = program.getFullURL(program.podcast, None)
                    # get the content
                    podcastXML = retriveURLContent(urlemission)
                    # get the podcast list, in the xml, and local
                    podcastInfo = parsePodcast(podcastXML, config, program.filemode)
                    
                    ### TODO must always clear the node element  : podcastInfo.localElementRoot

                    ##########################################
                    ### podcast empty 
                    if podcastInfo == None :
                        dialog2 = xbmcgui.Dialog()
                        dialog2.ok('Information', program.podcast + ' is empty...')
                    
                    ##########################################
                    # podcastInfo valid
                    else:
                        # Propose the list of available media
                        # TODO make a real window for presenting .. the description... etc image ... 
                        dialog2 = xbmcgui.Dialog()
                        eltIdx = dialog2.select( podcastInfo.title, podcastInfo.titles2display) 
                        #------------------------------------
                        # an element is selected
                        if eltIdx >= 0 and eltIdx < len(podcastInfo.itemsInfo):
                            
                            # the selected pod info
                            selPodItem = podcastInfo.itemsInfo[eltIdx]
                            
                            # read the prefs
                            mustDownload = program.mustDownload   # overrides global when defined
                            if mustDownload == None:
                                mustDownload = config.podcastDownload
                            
                            # if exist and finish always play
                            if os.path.exists(selPodItem.fileLocation) and selPodItem.flagfinish:
                                urlemission = selPodItem.fileLocation
                                mustDownload = False
                            #---------------                            
                                                           
                            # download activated and not a local file
                            if mustDownload and selPodItem.url != None and selPodItem.url != '':
                                
                                # try to create dir or pass if exist
                                if not createDirectory(podcastInfo.targetDirectory):
                                    raise MyCancel('Exit')
                                
                                # if exist and flag finished is true, use the local path
                                #if False and os.path.exists(selPodItem.fileLocation) and selPodItem.flagfinish:
                                #     urlemission = selPodItem.fileLocation   
                                                                                    
                                # file doesn't exist, or not fully downloaded, launch download or continue
                                #else:
                                # not fully downloaded
                                dlRet =  downloadFile(selPodItem.url, selPodItem.fileLocation, showDialog=False)
                                
                                ### TODO get a possible reditection..???
                                
                                if dlRet == -1 or dlRet == -2:
                                    # Can only stream this file, don't add this entry in the xml
                                    dialog3 = xbmcgui.Dialog()
                                    dialog3.ok('Information', 'The element cannot be downloaded','Will try to stream URL')            
                                    urlemission = selPodItem.url
                                    # error occur, cannot download, (mms:// or ..)
                                else:
                                    isfinished = dlRet == 1
                                    urlemission = selPodItem.fileLocation
                                    # add the entry to the index
                                    appendItem2Local(podcastInfo, selPodItem, isfinished)
                                        
                                    # download canceled by user
                                    if dlRet == 0:
                                        raise MyCancel('Exit')                                         
                        
                            #---------------
                            # url doesn't exist -> local file
                            elif selPodItem.url == None or selPodItem.url == '':  ### isLocal ?!
                                urlemission = selPodItem.fileLocation                                
                            #---------------
                            # streaming only                             
                            else:
                                urlemission = selPodItem.url
                                
                        #------------------------------------
                        # # Cancel the selection
                        else:
                            raise MyCancel('Exit') 

                else:
                    #--- Not a Podcast, Choose a Date -----
                    selectDate = getDiffusionDate(program) 
                    # if the date is None, getfull url will not replace thedate                       
                    urlemission = program.getFullURL(program.URLPattern, selectDate)
                    
                #-----------------------------------------------------------
                # Process the real media redirection
                urlemission = processRmFile(urlemission)
             
                if urlemission != None:
                    
                    ## TODO geturl to handle redirection, and remove always parameters after ? 
                    #outPrint('before:'+urlemission)
                    ## pas possible si: mms, rtsp:// ... 
                    #urlemission = getRedirection(urlemission)

                    ## TODO and remove all argument after ?
                    #outPrint('after:'+urlemission)
                    playURL(urlemission)

        except MyCancel, ex:
            #do nothing canceled
            pass 
        
        except Exception, ex:                        
            dialog2 = xbmcgui.Dialog()
            dialog2.ok('Information', 'Unexpected errors has occured...')            
            outPrint('unexpected errors has occured ', ex)


# the re pattern
RE_MEDIA_VERSION = re.compile('<?media.*?version\s*=\s*"(.*?)".*?>', re.DOTALL)

#----------------------------------------------------------------------------
class PrefsWindow(xbmcgui.Window):
    def __init__(self,config=None, mVersion=None):
        
        self.config = config
        self.mediaVersion = mVersion
        
        self.scaleX = ( float(self.getWidth())  / float(SIZE_WIDTH) )
        self.scaleY = ( float(self.getHeight()) / float(SIZE_HEIGHT) )
    
        self.addControl(xbmcgui.ControlImage(0, 0, self.getScX(SIZE_WIDTH), self.getScY(SIZE_HEIGHT), BACKGROUND))
    
        labelVersionInfo = xbmcgui.ControlLabel(self.getScX(305), self.getScY(110), self.getScX(200), self.getScY(30), "", "font13", "0xCCCCCCFF") 
        self.addControl(labelVersionInfo) 
        labelVersionInfo.setLabel('Configuration') 
        
        #####
        self.labelMediaPath1 =       xbmcgui.ControlLabel(self.getScX(100), self.getScY(200), self.getScX(150), self.getScY(30), "Podcast Folder", "font13", "0xCCCCCCFF") 
        self.addControl(self.labelMediaPath1) 
        
        self.browseLocalButton =     xbmcgui.ControlButton(self.getScX(280), self.getScY(195), self.getScX(100), self.getScY(30), 'Browse') 
        self.addControl(self.browseLocalButton)

        self.labelMediaPath =       xbmcgui.ControlLabel(self.getScX(100), self.getScY(240), self.getScX(600), self.getScY(30), "", "font13", "0xCCCCCCFF") 
        self.addControl(self.labelMediaPath) 
        
        self.labelMediaPath.setLabel(' > ' +self.config.podcastDownloadPath) 
        
        self.checkDownloadPodcast = xbmcgui.ControlCheckMark(self.getScX(100), self.getScY(280), self.getScX(300), self.getScY(30), "Download Podcasts When Possible?", font="font13", textColor="0xDDDDDDFF") 
        
        self.addControl(self.checkDownloadPodcast)  
        
        if self.config.podcastDownload:
            self.checkDownloadPodcast.setSelected(1)
        else:
            self.checkDownloadPodcast.setSelected(0)
               
        self.mediaButton =     xbmcgui.ControlButton(self.getScX(100), self.getScY(350), self.getScX(200), self.getScY(30), 'Update Media base') 
        self.addControl(self.mediaButton)
        
        self.aboutButton =     xbmcgui.ControlButton(self.getScX(100), self.getScY(400), self.getScX(100), self.getScY(30), 'About') 
        self.addControl(self.aboutButton)

        #####
        self.setFocus(self.browseLocalButton)

    # -------------------------------------------------------------------------------------------
    def getScY(self, y):
        return int(y * self.scaleY)
    def getScX(self, x):
        return int(x * self.scaleX)

    # -------------------------------------------------------------------------------------------
    def onAction(self, action):
        
        if (action == ACTION_PREVIOUS_MENU or action == ACTION_B) :
            saveScriptConfig(self.config)
            self.close()
      
        elif self.getFocus()  == self.browseLocalButton and action == ACTION_MOVE_DOWN :
            self.setFocus(self.checkDownloadPodcast)
        elif self.getFocus()  == self.checkDownloadPodcast and action == ACTION_MOVE_DOWN : 
            self.setFocus(self.mediaButton)
        elif self.getFocus()  == self.mediaButton and action == ACTION_MOVE_DOWN : 
            self.setFocus(self.aboutButton)
        elif self.getFocus()  == self.aboutButton and action == ACTION_MOVE_DOWN : 
            self.setFocus(self.browseLocalButton)
            
        elif self.getFocus()  == self.browseLocalButton and action == ACTION_MOVE_UP : 
            self.setFocus(self.aboutButton)
        elif self.getFocus()  == self.checkDownloadPodcast and action == ACTION_MOVE_UP : 
            self.setFocus(self.browseLocalButton)
        elif self.getFocus()  == self.mediaButton and action == ACTION_MOVE_UP : 
            self.setFocus(self.checkDownloadPodcast)
        elif self.getFocus()  == self.aboutButton and action == ACTION_MOVE_UP : 
            self.setFocus(self.mediaButton)
            

    # -------------------------------------------------------------------------------------------
    def onControl(self, control):
        
        try:
            if control == self.browseLocalButton:
                
                ## set the new local download path
                newPath = xbmcgui.Dialog().browse(0,"a Directory","files")
                if newPath != None and len(newPath) > 0:
                    # is set in the main config of the root window, but is saved in the file when closing window
                    self.config.podcastDownloadPath = newPath
                    self.labelMediaPath.setLabel(' > ' + newPath) 
    
            elif control == self.mediaButton:
                # load the media.xml and exit...
                redown = downloadFile(self.config.mediaUpdateURL, MEDIA_TMP_CONF, 0)
                if redown == 1 and os.path.exists(MEDIA_TMP_CONF):
                    # test the media file, and version
                    startf = readFile(MEDIA_TMP_CONF, 10000)
                    newMediaVersion = "0.0"
                    versionRet = RE_MEDIA_VERSION.findall(startf)
                    if versionRet and versionRet[0]  :
                        newMediaVersion = versionRet[0]
                    
                    if self.mediaVersion < newMediaVersion:
                        # rename the orig file, and 
                        oldmedia = MEDIA_CONF + '_old_'+ self.mediaVersion
                        #delete old if exist
                        if os.path.exists(oldmedia):
                            os.remove(oldmedia)
                            
                        os.rename(MEDIA_CONF, oldmedia)
                        os.rename(MEDIA_TMP_CONF, MEDIA_CONF)
        
                        dialog2 = xbmcgui.Dialog()
                        dialog2.ok('Media file has been updated', '', 'Please Restart MediaStream !')  

                    else:
                        dialog2 = xbmcgui.Dialog()
                        dialog2.ok('Information', 'No new version available...')  
    
                # Delete tmp file when not renamed to new file
                if os.path.exists(MEDIA_TMP_CONF):
                    os.remove(MEDIA_TMP_CONF)
    
            elif control == self.checkDownloadPodcast:
                self.config.podcastDownload = self.checkDownloadPodcast.getSelected() == 1
            
            elif control == self.aboutButton:
                dialog = xbmcgui.Dialog()
                dialog.ok('About', 'Media Stream v. %s'%(VERSION),'Contact me at oli@euromobile.ch')
        
        except Exception, ex:                        
            dialog2 = xbmcgui.Dialog()
            dialog2.ok('Information', 'Unexpected errors has occured...')            
            outPrint('unexpected errors has occured ', ex)  
  

#----------------------------------------------------------------------------
class RootWindow(xbmcgui.Window):
    def __init__(self):
        #self.setCoordinateResolution(6)
    
        self.scaleX = ( float(self.getWidth())  / float(SIZE_WIDTH) )
        self.scaleY = ( float(self.getHeight()) / float(SIZE_HEIGHT) )
        
        try:
            self.mainConfig = readScriptConfig()                      
        except Exception, ex:
            outPrint('Unable to init the config, use the default', ex)
            self.mainConfig  = UserConfig(None,None,None,None)

        try:
            self.channels, self.categories, self.mediaVersion = readMediaElementTree(MEDIA_CONF, ENCODING_OUT)            
        except Exception, ex:
            outPrint('Unable to init the channel list', ex)
            return
        
        self.addControl(xbmcgui.ControlImage(0, 0, self.getScX(SIZE_WIDTH), self.getScY(SIZE_HEIGHT), BACKGROUND))
    
        self.strVersionInfo = xbmcgui.ControlLabel(self.getScX(315), self.getScY(110), self.getScX(200), self.getScY(200), "", "font12", "0xCCCCCCFF") 
        self.addControl(self.strVersionInfo)
        
        self.strVersionInfo.setLabel('Version %s'%(VERSION) ) 
    
        self.list = xbmcgui.ControlList(self.getScX(83), self.getScY(140), self.getScX(548), self.getScY(400),
                                        buttonTexture=LIST_SELECT_BG,
                                        buttonFocusTexture=LIST_SELECT_BG_FOCUS,
                                        textColor='0xFFFFFFFF',
                                        itemHeight=self.getScY(70),
                                        space=5,
                                        itemTextXOffset=self.getScX(40),
                                        imageWidth=self.getScX(74),
                                        imageHeight=self.getScY(50)
                                        )        
        self.addControl(self.list)
        
        #the stack of all entered elements, category or channel
        self.listElements = []
        elements = []
        
        # add the root categories, no parent, and also the channels without a category
        for category in self.categories:
            if category.parentid == None:
                self.list.addItem(xbmcgui.ListItem(category.name , thumbnailImage=os.path.join(IMAGES, category.imagelink))) 
                elements.append(category)   
        
        # add the channels
        for channel in self.channels:
            if channel.categoryId == None:
                chanstr = channel.name
                if channel.description and len(channel.description) > 1:
                    chanstr = chanstr + '\n  '+ channel.description
                self.list.addItem(xbmcgui.ListItem(chanstr, thumbnailImage=os.path.join(IMAGES, channel.imagelink)))
                elements.append(channel)   
 
        # append the list into the element list...
        self.listElements.append(elements)
        self.listTitles = []
        self.listTitles.append('Version %s'%(VERSION))
        
        # Focus
        self.setFocus(self.list)

    def getScY(self, y):
        return int(y * self.scaleY)

    def getScX(self, x):
        return int(x * self.scaleX)
    
    # -------------------------------------------------------------------------------------------
    def onAction(self, action):
        try:
            if (action == ACTION_PREVIOUS_MENU or action == ACTION_B) :
                if self.listElements != None and len(self.listElements) > 1 :
                    
                    #pop the last list of elements
                    lastlist = self.listElements.pop(len(self.listElements) -1)
                    self.listTitles.pop(len(self.listTitles) -1)
                    
                    self.list.reset()
                    
                    # get the list of parent elements to display now
                    newlist = self.listElements[len(self.listElements) -1]
                    newTitle = self.listTitles[len(self.listTitles) -1]
                    #self.strVersionInfo.setLabel(newTitle ) 
                    
                    # add all elements into the control list
                    for selElement in newlist:
                        if isinstance(selElement, Category) :
                            # a Category
                            category = selElement
                            self.list.addItem(xbmcgui.ListItem(category.name , thumbnailImage=os.path.join(IMAGES, category.imagelink))) 
                        else: 
                            # a channel
                            channel = selElement
                            chanstr = channel.name
                            if channel.description and len(channel.description) > 1:
                                chanstr = chanstr + '\n  '+ channel.description
                            self.list.addItem(xbmcgui.ListItem(chanstr, thumbnailImage=os.path.join(IMAGES,channel.imagelink)))
                else:
                    # root level, quit the script, TODO add a window
                    self.close()
        
            if action == ACTION_Y or action == ACTION_INFO:
                win = PrefsWindow(config=self.mainConfig, mVersion=self.mediaVersion)         
                win.doModal() 
                del win 

        except Exception, ex:
            outPrint('unexpected error rootwin', ex)
                
    # -------------------------------------------------------------------------------------------
    def onControl(self, control=None):
        try:            
            if control == self.list and len(self.listElements) > 0 and self.listElements[len(self.listElements) -1]:
                # get the last list of elements, the displayed list
                elements = self.listElements[len(self.listElements) -1]
                # get the selected element
                selElement = elements[self.list.getSelectedPosition()]            
                
                # the new selected list of alement
                newElements = []
                
                # a category selected
                if isinstance(selElement, Category) :
                    parentcategory =  selElement
                    self.listElements.append(newElements)
                    self.listTitles.append(parentcategory.name)
                    #self.strVersionInfo.setLabel(parentcategory.name )
                     
                    self.list.reset()
                    
                    # add the categories
                    for category in self.categories:
                        if category.parentid == parentcategory.id:
                            self.list.addItem(xbmcgui.ListItem(category.name , thumbnailImage=os.path.join(IMAGES,category.imagelink))) 
                            newElements.append(category)   
                    
                    # add the channels
                    for channel in self.channels:
                        if channel.categoryId == parentcategory.id:
                            chanstr = channel.name
                            if channel.description and len(channel.description) > 1:
                                chanstr = chanstr + '\n  '+ channel.description
                            self.list.addItem(xbmcgui.ListItem(chanstr, thumbnailImage=os.path.join(IMAGES,channel.imagelink)))
                            newElements.append(channel)                   
                                        
                elif isinstance(selElement, Channel) :
                    #if the selection is not a category -> a channel
                    channel =  selElement
                    self.channel = channel
                    
                    channel.optionsSelectedValue = chooseOptions(channel.options)
                    
                    # open a sub window for a specific channel
                    channelWin = ChannelWindow(rootwin=self)            
                    channelWin.doModal() 
                    del channelWin 

        ## TODO change by a new exception..
        except MyCancel, ex:
            #outPrint('Canceled ?!', ex)
            pass #do nothing canceled
        
        except Exception, ex:
            outPrint('unexpected error rootwin', ex)


# Main -------------------------------------------------------------------------------------------

gc.enable()

rootWin = None
dialog = None
try:
    dialog = xbmcgui.DialogProgress()
    dialog.create('MediaStream', 'Loading media...')
    
    rootWin = RootWindow()
    
    dialog.close()
    rootWin.doModal()
    del rootWin  
except Exception, ex:
    outPrint('unexpected error main', ex)
        
    if dialog :
        dialog.close()       
    #if rootWin :
    #    rootWin.close()
    #    del rootWin
        
        