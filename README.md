iBooks-KF8
==========

Python script to convert iBooks fixed layout to KF8 files and add text magnification boxes

  * You can convert multiple files at the same time. Just put them all in the files folder.
  
###############

THIS IS A WORK IN PROGRESS, BUT IT WORKS

If anyone has any suggestions for simplifying this code it would be gratefully recieved.
It does work, as long as all the conditions below are met.
If you run into any serious issues let me know.

  * File for conversion must be placed in /files folder
  * Output place in /repubbed folder
  * Sample file is included in repository
  
Usage: Navigate to 'script' folder in the command line, then type "python ibooks_kf8.py"

Guidelines for text magnification:
  
  * Each block of text that is to be magnified must be surrounded by a div with a unique class of the pattern pg_##_mag_## eg pg_01_mag_01 (you can change this pattern in the code, simply search for "div_finder" and alter the regex. Positioning and text sizing should be done by styling this containing div:
  
  	<div class="pg_01_mag_01">
        <p class="p1Text001">This text should appear between the top and middle lines in a normal font.</p>
	</div>
    <div class="pg_01_mag_02">
        <p class="p1Text002">This text should appear between the middle and bottom lines in Rosewood.</p>
    </div>
  
  * ALL POSITIONING MUST BE DONE IN PERCENTAGES, AND FONT SIZES IN EMS
  * ALL CONTAINER DIVS MUST BE POSITIONED ABSOLUTELY  
  * You can alter the CSS for the text mag boxes by searching for "mag_boxes"
  * By default the text-mag boxes will be positioned 2% less on top and left
  * By default font-size for magnified text is 2 * original em value
  * You can change these defaults by searching for "topleft" and "fontsizing"
  
Things you need for this to work:

  * Python 3+ and BeautifulSoup4 module installed
  * Folder structure must be as it is on git
  * Content files must be .xhtml
  * Cover page should be called cover.xhtml
  * Must include a reset css file called reset.css
  * All other styles must be in stylesheet.css file. Only 1 master stylesheet allowed
  * Styles should be placed in folder named /css
  * Best to use RGB Jpg files. Transparent PNG files won't work at all.
  
Things it doesn't do:
  
  * Resolve internal or TOC links: If you have a full NCX TOC the links will have to be changed by hand. The same for HTML TOCs and other internal links
  * Guarantee that things will work: Especially when it comes to SVG. Very likely you'll have to re-do or at least tweak SVG text.
  * Resize anything: Everything will be the same size as it was in iBooks. 