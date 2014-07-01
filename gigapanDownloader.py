#usage: python downloadGigaPan.py <photoid> <level>
# http://gigapan.org/gigapans/<photoid>>
# if level is 0, max resolution will be used, try with different levels to see the image resolution to download
# change imagemagick or outputformat below
# Project info https://github.com/DeniR/Gigapan-Downloader-and-stitcher

import xml.etree.ElementTree as ET
from urllib2 import *
from urllib import *
import sys,os,math,subprocess


outputFormat="tif" #psb or tif
imageMagick="/usr/bin/montage" #Linux path to Imagemagick
if os.name == "nt":
	imageMagick="C:\\Program Files\\ImageMagick-6.8.5-Q16\\montage.exe" #Windows path to Imagemagick


# -------------------------------------------------- Get Arguments --------------------------------------------------

givenID = str(sys.argv[1]) # Can be an hex ID
givenLevel = int(sys.argv[2])


# -------------------------------------------------- Get KML with information --------------------------------------------------

KML = urlopen("http://www.gigapan.org/gigapans/%s.kml"%(givenID))
KMLString = KML.read()
KMLElementRoot = ET.fromstring(KMLString)
#tree = ET.parse('ejemplo.kml')
#KMLElementRoot = tree.getroot()
KMLNamespace = KMLElementRoot.tag.strip("}kml").strip("{") # Get namespace by removing tag and brackets, namespace is used as a prefix in tags


# -------------------------------------------------- Navigation through KML to get information --------------------------------------------------

KMLElementPhotoOverlay = KMLElementRoot[0].find("{"+KMLNamespace+"}PhotoOverlay") # Locating PhotoOverlay tag, which contains all the information useful to us
KMLElementImagePyramid = KMLElementPhotoOverlay.find("{"+KMLNamespace+"}ImagePyramid") # Locating ImagePyramid tag
KMLElementIcon = KMLElementPhotoOverlay.find("{"+KMLNamespace+"}Icon") # Locating Icon tag

IDString = KMLElementPhotoOverlay.attrib["id"] # Image ID can be found as an attribute of PhotoOverlay
ID = int(IDString.strip("gigapan_")) # Remove "gigapan_" prefix and convert to int
maxWidth = int(KMLElementImagePyramid.find("{"+KMLNamespace+"}maxWidth").text) # Image width in pixels for higher level
maxHeight = int(KMLElementImagePyramid.find("{"+KMLNamespace+"}maxHeight").text) # Image height in pixels for higher level
tileSize = int(KMLElementImagePyramid.find("{"+KMLNamespace+"}tileSize").text) # Size of tiles in pixels
tilesURL = KMLElementIcon.find("{"+KMLNamespace+"}href").text


# -------------------------------------------------- Calculation of image properties --------------------------------------------------

maxWidthTiles = int(math.ceil(maxWidth/tileSize)) + 1 # Image width in tiles for higher level
maxHeightTiles = int(math.ceil(maxHeight/tileSize)) + 1 # Image height in tiles for higher level

maxLevel = max(math.ceil(maxWidth/tileSize), math.ceil(maxHeight/tileSize))
maxLevel = int(math.ceil(math.log(maxLevel)/math.log(2.0)))

if givenLevel == 0: 
	level = maxLevel
else:
	level = givenLevel

width = int(maxWidth / (2 ** (maxLevel-level)))+1 # Image width in pixels
height = int(maxHeight / (2 ** (maxLevel-level)))+1 # Image height in pixels
widthTiles = int(math.ceil(width/tileSize))+1 # Image width in tiles
heightTiles = int(math.ceil(height/tileSize))+1 # Image height in tiles

tilesURL = tilesURL.replace("$[level]", str(level)) # Placing ID in tiles URL


# -------------------------------------------------- Create tiles folder if necessary --------------------------------------------------

if not os.path.exists(str(ID)):
	os.makedirs(str(ID))


# -------------------------------------------------- Print the variables --------------------------------------------------
print "Gigapan image properties:"
print "   Max size: %dx%dpx"%(maxWidth, maxHeight)
print "   Max number of tiles: %dx%d tiles = %d tiles"%(maxWidthTiles, maxHeightTiles, maxWidthTiles*maxHeightTiles)
print "   Max resolution level: %d"%(maxLevel)
print ""
print "Arguments given:"
print "   ID: %s"%(givenID)
print "   Resolution level: %d"%(givenLevel)
print ""
print "Image to download:"
print "   ID: %s"%(ID)
print "   Size: %dx%dpx"%(width, height)
print "   Number of tiles: %dx%d tiles = %d tiles"%(widthTiles, heightTiles, widthTiles*heightTiles)
print "   Resolution level: %d"%(level)
print ""
print "Starting Download..."
print ""


# -------------------------------------------------- Loop around to get every tile --------------------------------------------------
for j in xrange(heightTiles):
	for i in xrange(widthTiles):
		filename = "%04d-%04d.jpg"%(j,i)
		pathFilename = str(ID)+"/"+filename
		if not os.path.exists(pathFilename) :
			URL = tilesURL.replace("$[y]", str(j)) # Place j in URL
			URL = URL.replace("$[x]", str(i)) # Place i in URL
			progress = j*widthTiles+i+1 # Calculate tiles downloaded
			print '('+str(progress)+'/'+str(widthTiles*heightTiles)+') Downloading '+str(URL)+' as '+str(filename) 
			h = urlopen(URL)
			fout = open(pathFilename,"wb")
			fout.write(h.read())
			fout.close()
print "Stitching... "
subprocess.call('"'+imageMagick+'" -depth 8 -geometry 256x256+0+0 -mode concatenate -tile '+str(widthTiles)+'x '+str(ID)+'/*.jpg '+str(ID)+'-giga.'+outputFormat, shell=True)
print "Finished!"