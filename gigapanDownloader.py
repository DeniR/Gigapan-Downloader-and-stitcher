#usage: python downloadGigaPan.py <photoid>
# http://gigapan.org/gigapans/<photoid>>
# change imagemagick or outputformat below
# Project info https://github.com/DeniR/Gigapan-Downloader-and-stitcher

from xml.dom.minidom import *
from urllib2 import *
from urllib import *
import sys,os,math,subprocess

outputformat="psb" #psb or tif
imagemagick="/usr/local/bin/montage" #Linux path to Imagemagick
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

height=int(find_element_value(dom.documentElement, "maxHeight"))
width=int(find_element_value(dom.documentElement, "maxWidth"))
tile_size=int(find_element_value(dom.documentElement, "tileSize"))

print width,height,tile_size


maxlevel = max(math.ceil(width/tile_size), math.ceil(height/tile_size))
maxlevel = int(math.ceil(math.log(maxlevel)/math.log(2.0)))
wt = int(math.ceil(width/tile_size))+1
ht = int(math.ceil(height/tile_size))+1
print wt,ht,maxlevel

#loop around to get every tile
for j in xrange(ht):
    for i in xrange(wt):
        filename = "%04d-%04d.jpg"%(j,i)
	pathfilename = str(photo_id)+"/"+filename
	if not os.path.exists(pathfilename) :
	        url = "%s/get_ge_tile/%d/%d/%d/%d"%(base,photo_id, maxlevel,j,i)
	        print url, filename
	        h = urlopen(url)
	        fout = open(pathfilename,"wb")
	        fout.write(h.read())
	        fout.close()
print "Stitching... "
subprocess.call('"'+imagemagick+'" -depth 8 -geometry 256x256+0+0 -mode concatenate -tile '+str(wt)+'x '+str(photo_id)+'\*.jpg '+str(photo_id)+'-giga.'+outputformat, shell=True)
print "OK"
