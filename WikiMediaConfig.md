# Configuration Properties #
```
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
 download            : boolean flag that overrides the global preference

 ----------------------------------------------------
 Replacement keys (can be used in baseURL and URL)
 ----------------------------------------------------
 $DAY			: day indentifier 00-31
 $MONTH			: month identifier 00-12
 $YEAR2			: year identifier in 2 decimals, e.g. 07
 $YEAR4			: year identifier in 4 decimals, e.g. 2007
 $CH_OPTIONi	: optional value selected by the user from the channel 'options' value
 $PR_OPTIONi	: optional value selected by the user from the program 'prooptions' value

```

# Example of media.xml file #

```

<?xml version="1.0" encoding="iso-8859-1"?>
<media version="0.85b" author="oli_AT_euromobile.ch" date="18.08.2008" >
	
	<category id="ch" imagelink="dp\dp_suisse.jpg">Switzerland</category>

	<channel baseurl="http://www.tsr.ch/xobix_media/tsr" imagelink="tsr\tsr.jpg" category="ch">

		<name>TSR</name>
		<description>Télévision Suisse Romande</description>
				
		<option>
			<descr>Archive Quality</descr>
			<item value="501k">High 16/9</item>
		</option>

		<program ispodcast="true" 
			url="http://xml.tsr.ch/xml/index.xml?siteSect=674000&amp;programId=$PR_OPTION1">
			
			<name>TSR (Podcast)</name>
			<prooption>
				<descr>Emissions</descr>
				<item value="55">Temps Présent</item>
				<item value="90">Nouvo</item>
				<item value="235939">Nouvo (Minute)</item>
			</prooption>
		</program>

		<program imagelink="tsr\info.jpg"
			url="$URL/$PR_OPTION1/$YEAR4/$PR_OPTION1_$MONTH$DAY$YEAR4-$CH_OPTION1.flv">
			<name>Le Journal</name>
			<diffusion id="7"/>
			<prooption>
				<descr>Edition</descr>
				<item value="tj">TJ 19h30</item>
				<item value="rg">Journal des Régions (19h)</item>
				<!-- item value="tj_midi">Journal de 12h45</item-->
			</prooption>
		</program>

	</channel>
</media>
```