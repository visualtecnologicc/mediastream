#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os, xbmc

XBMC_USER_DATA       = xbmc.translatePath('T:\\')
HOME                 = os.getcwd().replace(';','')

# default directory where are saved the media file
# you can change it here or in the preference
MEDIA_PODCAST_DIR    =  os.path.join(HOME,'Podcasts')
# update url
MEDIA_UPDATE_URL     = 'http://olivier.euromobile.ch/mediastream/media.xml'
# config file
CONFIG_DIR_ROOT      = os.path.join(XBMC_USER_DATA, 'script_data', 'mediastream')
CONFIG_FULL_PATH     = os.path.join(CONFIG_DIR_ROOT, 'userconfig.xml')
# media file
MEDIA_CONF           = os.path.join(HOME, 'media.xml')
MEDIA_TMP_CONF       = os.path.join(HOME, '_tempmedia.xml')

VERSION              = '0.92'

PODCAST_DOWNLOAD     = True

# LOG LEVEL:
# 0 no print, no log
# 1 print
# 2 print, exception
# 3 log to file "debug.log" -> problem on osx
LOG_VALUE = 3

# FIX ME !!
DEBUG_FILE           = os.path.join(HOME, 'debug.log')

SIZE_WIDTH           = 720
SIZE_HEIGHT          = 576
ENCODING_OUT         = 'iso-8859-1'
ENCODING_IN          = 'utf-8'        # for parsing xml using minidom

IMAGES               = os.path.join(HOME,'images')
BACKGROUND           = os.path.join(IMAGES,'background.png')
BACKGROUND2          = os.path.join(IMAGES,'background2.png')
LIST_SELECT_BG       = os.path.join(IMAGES,'listbg.png')
LIST_SELECT_BG_FOCUS = os.path.join(IMAGES,'listbg_focus.png')

DEF_CHANNEL_PIC      = 'defchannel.png'
DEF_PROGRAM_PIC      = 'defprogram.png'

# Codes keymap
ACTION_PREVIOUS_MENU    = 10
ACTION_SELECT_ITEM      = 7
ACTION_MOVE_LEFT        = 1
ACTION_MOVE_RIGHT       = 2
ACTION_MOVE_UP          = 3
ACTION_MOVE_DOWN        = 4
ACTION_X                = 18
ACTION_B                = 9
ACTION_Y                = 34

ACTION_LTRIGGER = 5
ACTION_RTRIGGER = 6
ACTION_B        = 9
ACTION_Y        = 18
ACTION_INFO     = 11
ACTION_PAUSE    = 12
ACTION_STOP     = 13

