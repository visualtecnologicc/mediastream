#####################################################
#         Media Stream script for XBMC by Oliv      #
#                Version 0.91                       #
#              oli AT euromobile.ch                 #
##################################################### 

Media Stream is an XBMC script for streaming / downloading audio, videos and RSS podcasts.
The following topic can be used for more information:

http://code.google.com/p/mediastream/ 
http://gueux-forum.net/index.php?showtopic=146820
http://passion-xbmc.org/scripts/mediastream
 
You can send me Radio/TV/Podcasts accessing information and I will add them to the script, 
please read the configuration tips below, and enter your settings into the file media.xml

##################################################### 
 Usage:
	- For Accessing to the preference window, press Y in the root window or "i" in non-XBOX platforms
	- You can also edit modules/constants.py for specifying a configuration

##################################################### 
 History:

   Version 0.91
    - Added new media entries (streams, podcasts)
    - reorganized some categories 
    - temporary fix in order to be compatible with last release of XBMC on Linux, Windows 
      and Mac since append on file ('a+') in currently broken in XBMC
      
   Version 0.90
    - clean and add media entries into media.xml (Thanks to Temhil)

   Version 0.87b
    - add streaming/download choice in each entry of media.xml

    Version 0.86
    - fix the user config saving (location on all platforms)
    - fix reload flag download podcast

    Version 0.85b
    - fix a path problem with XBMC beta multi platform (Thanks to Temhil)

    Version 0.85
    - fix a problem with the storing of the configuration of podcast properties.
    - fix tsr channels rm -> flv

    Version 0.84
    - fix a bug on new beta XBMC

    Version 0.83
    - updated media canaplus, and name dir filter

    Version 0.82
    - updated witv.com base
    - fixed the images positionning
    - fixed user directory creation

    Version 0.81
    - added images (thanks dekani)
    - fixed when image not available -> use default

    Version 0.8
    - added user properties
    - added preference window, press Y
    - added internet update of media.xml
    - Modification of the podcast management, only one xml report file foreach item
    - Modularization and cleaning
    - Portugal radio added (thanks to cfjrocha@gmail.com)
    
    Version 0.7c
    - added images (thanks dekani)
    - added witv TV stream (thanks to Gan)
    - conversion to elementTree xml
    
    Version 0.7b
    - continue downloading when canceled
    - added the list of podcast also include the already downloaded podcast
    - added a flag for downloading or not podcast in the program window
    - updated media german entries (thanks to warsheep)
    - fix a problem when accessing to podcasts with option in the url
    
    Version 0.7
    - added reading podcast using xml dom, fix the decoding problem
    - added using xml for the media config file
    - added multiresolution
    - add sub categories, in the channel window and in the program window (like hierarchical categories folders)
    
    Version 0.6
    - fix a bug when listening podcast mp3 -> download
    - added RSS podcast support (w downloading)
    - added multiple list of options with labels and titles
    - added availability of a program
    - added M6infos thanks to Dekani (script M6Infos)
    - added Tf1 JT, podcast
    - added divers podcast

    Version 0.5
    - added externalization of the media config    
    

##################################################### 
 Media Configuration: 
 
 (Documentation about the xml file will be improved soon, if you need more explainations ask me for questions)
 
 ----------------------------------------------------
 Channel parameters
 ----------------------------------------------------
 name			: the string name of the channel (mandatory)
 baseurl		: base url (string), accessible in a program URL value with '$URL' (and '$URL2' when come from the options?)
 options   		: a list of option, defined using a dico, selected value -> '$CH_OPTIONi', i = 1->n
 desc			: the description string
 imagelink		: the image relative path in from dir 'images'
 category		: the category id
 
 ----------------------------------------------------
 Program parameters
 ----------------------------------------------------
 name			: the string name of the channel (mandatory)
 url			: url (string) of the program (can use string replacement keys, as $MONTH, $URL, ..)
 prooption	    : list of option, defined using a dico, selected value -> '$PR_OPTIONi', i = 1->n
 desc			: the description string
 imagelink		: the image relative path in from dir 'images'
 diffusion		: the diffusion time (string list, by default  '-1'), can be cumulated e.g. '0','2' -> monday and wednesday
 	'-1'		: live (no dated archived)
 	'0'->'6'	: hebdo, a specific day, monday:'0' -> sunday:'6' 
 	'7'			: all days 
 	'8'			: monday -> friday
 	'9'			: saturday -> sunday
 avail			: Availaility of the program, 
					start -> the older possible date	
					nbdays -> the maximum of days where a program is available 
					nbdiff -> the maximum available diffusions 
 ispodcast		: boolean flag
 filemode="title" : for podcast, to force the file name to download to be built with the title
 download       : boolean flag that overrides the global preference

 ----------------------------------------------------
 Replacement keys (can be used in baseURL and URL)
 ----------------------------------------------------
 $DAY			: day indentifier 00-31
 $MONTH			: month identifier 00-12
 $YEAR2			: year identifier in 2 decimals, e.g. 07
 $YEAR4			: year identifier in 4 decimals, e.g. 2007
 $CH_OPTIONi	: optional value selected by the user from the channel 'options' value
 $PR_OPTIONi	: optional value selected by the user from the program 'prooptions' value

 

