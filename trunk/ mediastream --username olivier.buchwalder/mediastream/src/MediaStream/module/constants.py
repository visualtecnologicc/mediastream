#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os

##############################################
# User Parameters

# The directory where are saved the media file
MEDIA_PODCAST_DIR      = 'F:\\media\\Podcasts\\'
MEDIA_PODCAST_DIR_ALT  = 'E:\\media\\Podcasts\\'
MEDIA_UPDATE_URL       = 'http://olivier.euromobile.ch/mediastream/media.xml'

##############################################
# The current version
VERSION                = '0.85'

##############################################
# 0 no print, no log
# 1 print
# 2 print, exception
# 3 log to file "debug.log"
LOG_VALUE = 3

##############################################
# Script Properties

PODCAST_DOWNLOAD     = True

MEDIA_CONF           = 'media.xml'
MEDIA_TMP_CONF       = '_tempmedia.xml'

HOME                 = os.getcwd()[:-1]+'\\'

CONFIG_DIR_ROOT      = 'P:\\script_data\\'
CONFIG_DIR_MEDIA     = 'mediastream\\'

CONFIG_DIR           = CONFIG_DIR_ROOT + CONFIG_DIR_MEDIA
CONFIG_FULL_PATH     = CONFIG_DIR + "userconfig.xml"

SIZE_WIDTH           = 720
SIZE_HEIGHT          = 576
ENCODING_OUT         = 'iso-8859-1'
ENCODING_IN          = 'utf-8'        # for parsing xml using minidom

IMAGES               = HOME+'images\\'
BACKGROUND           = IMAGES+'background.png'
BACKGROUND2          = IMAGES+'background2.png'
LIST_SELECT_BG       = IMAGES+'listbg.png'
LIST_SELECT_BG_FOCUS = IMAGES+'listbg_focus.png'

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

