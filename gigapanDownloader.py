#usage: python downloadGigaPan.py <photoid>
# http://gigapan.org/gigapans/<photoid>>
# if level is 0, max resolution will be used, try with different levels to see the image resolution to download
# change imagemagick or outputformat below
# Project info https://github.com/DeniR/Gigapan-Downloader-and-stitcher

from xml.dom.minidom import *
from urllib2 import *
from urllib import *
import sys,os,math,subprocess

outputformat="psb" #psb or tif
imagemagick="/usr/bin/montage" #Linux path to Imagemagick
if os.name == "nt":
  imagemagick="C:\\Program Files\\ImageMagick-6.8.5-Q16\\montage.exe" #Windows path to Imagemagick

def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def find_element_value(e,name):
    nodelist = [e]
    while len(nodelist) > 0 :
        node = nodelist.pop()
        if node.nodeType == node.ELEMENT_NODE and node.localName == name:
            return getText(node.childNodes)
        else:
            nodelist += node.childNodes

    return None


#main

photo_id = int(sys.argv[1])
if not os.path.exists(str(photo_id)):
    os.makedirs(str(photo_id))

base = "http://www.gigapan.org"

# read the kml file
h = urlopen(base+"/gigapans/%d.kml"%(photo_id))
photo_kml=h.read()

# find the width and height, level 
dom = parseString(photo_kml)

maxheight=int(find_element_value(dom.documentElement, "maxHeight"))
maxwidth=int(find_element_value(dom.documentElement, "maxWidth"))
tile_size=int(find_element_value(dom.documentElement, "tileSize"))
maxlevel = max(math.ceil(maxwidth/tile_size), math.ceil(maxheight/tile_size))
maxlevel = int(math.ceil(math.log(maxlevel)/math.log(2.0)))
maxwt = int(math.ceil(maxwidth/tile_size))+1
maxht = int(math.ceil(maxheight/tile_size))+1

# find the width, height, tile number and level to use
level = int(sys.argv[2])
if level == 0: 
  level = maxlevel

width = int(maxwidth / (2 ** (maxlevel-level)))+1
height = int(maxheight / (2 ** (maxlevel-level)))+1
wt = int(math.ceil(width/tile_size))+1
ht = int(math.ceil(height/tile_size))+1

# print the variables
print '+----------------------------'
print '| Max size: '+str(maxwidth)+'x'+str(maxheight)+'px'
print '| Max number of tiles: '+str(maxwt)+'x'+str(maxht)+' tiles = '+str(wt*ht)+' tiles'
print '| Max level: '+str(maxlevel)
print '| Tile size: '+str(tile_size)
print '+----------------------------'
print '| Image to download:'
print '| Size: '+str(width)+'x'+str(height)+'px'
print '| Number of tiles: '+str(wt)+'x'+str(ht)+' tiles = '+str(wt*ht)+' tiles'
print '| Level: '+str(level)
print '+----------------------------'
print
print 'Starting download...'

#loop around to get every tile
for j in xrange(ht):
    for i in xrange(wt):
        filename = "%04d-%04d.jpg"%(j,i)
	pathfilename = str(photo_id)+"/"+filename
	if not os.path.exists(pathfilename) :
	        url = "%s/get_ge_tile/%d/%d/%d/%d"%(base,photo_id, level,j,i)
	        progress = (j)*wt+i+1
	        print '('+str(progress)+'/'+str(wt*ht)+') Downloading '+str(url)+' as '+str(filename)
	        h = urlopen(url)
	        fout = open(pathfilename,"wb")
	        fout.write(h.read())
	        fout.close()
print "Stitching... "
subprocess.call('"'+imagemagick+'" -depth 8 -geometry 256x256+0+0 -mode concatenate -tile '+str(wt)+'x '+str(photo_id)+'\*.jpg '+str(photo_id)+'-giga.'+outputformat, shell=True)
print "OK"
