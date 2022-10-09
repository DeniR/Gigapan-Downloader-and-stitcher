#!/usr/bin/env python3

# Usage:
#     gigapan_downloader.py -h
#
# Normally links are:
#     http://gigapan.org/gigapans/<img_name>>
#
# if level is 0, max resolution will be used, try with different levels to see
# the image resolution to download
#
# Change imagemagick or outputformat below
# Project info: https://github.com/DeniR/Gigapan-Downloader-and-stitcher

import xml.etree.ElementTree as ElementTree
import urllib.request
import argparse
import os
from pathlib import Path
import math
import subprocess

output_format = "tif" # psb or tif
montage_command = "/usr/bin/montage" # Linux path to Imagemagick
if os.name == "nt":
    montage_command = "C:\\Program Files\\ImageMagick-6.8.5-Q16\\montage.exe" # Windows path to Imagemagick


def parse_kml(kml_string):

    KMLElementRoot = ElementTree.fromstring(kml_string)
    # Get namespace by removing tag and brackets, namespace is used as a prefix in tags
    KMLNamespace = KMLElementRoot.tag.strip("}kml").strip("{")

    # Locating PhotoOverlay tag, which contains all the information useful to us
    KMLElementPhotoOverlay = KMLElementRoot[0].find("{"+KMLNamespace+"}PhotoOverlay")
    # Locating ImagePyramid tag
    KMLElementImagePyramid = KMLElementPhotoOverlay.find("{"+KMLNamespace+"}ImagePyramid")
    # Locating Icon tag
    KMLElementIcon = KMLElementPhotoOverlay.find("{"+KMLNamespace+"}Icon")

    # Image ID can be found as an attribute of PhotoOverlay
    id_string = KMLElementPhotoOverlay.attrib["id"]
    # Remove "gigapan_" prefix and convert to int
    img_id = int(id_string.strip("gigapan_"))
    # Image width in pixels for higher level
    max_width_px = int(KMLElementImagePyramid.find("{"+KMLNamespace+"}maxWidth").text)
    # Image height in pixels for higher level
    max_height_px = int(KMLElementImagePyramid.find("{"+KMLNamespace+"}maxHeight").text)
    # Size of tiles in pixels
    tile_size_px = int(KMLElementImagePyramid.find("{"+KMLNamespace+"}tileSize").text)
    tiles_url = KMLElementIcon.find("{"+KMLNamespace+"}href").text

    return img_id, tiles_url, (max_width_px, max_height_px), tile_size_px

def calculate_max_size(max_width_px, max_height_px, tile_size_px):
    # Image width in tiles for higher level
    max_width_tiles = int(math.ceil(max_width_px/tile_size_px)) + 1
    # Image height in tiles for higher level
    max_height_tiles = int(math.ceil(max_height_px/tile_size_px)) + 1

    max_level = max(math.ceil(max_width_px/tile_size_px), math.ceil(max_height_px/tile_size_px))
    max_level = int(math.ceil(math.log(max_level)/math.log(2.0)))

    return (max_width_tiles, max_height_tiles), max_level

def calculate_size(max_width_px, max_height_px, tile_size_px, max_level, level):

    width_px = int(max_width_px / (2 ** (max_level-level))) + 1 # Image width in pixels
    height_px = int(max_height_px / (2 ** (max_level-level))) + 1 # Image height in pixels
    width_tiles = int(math.ceil(width_px/tile_size_px)) + 1 # Image width in tiles
    height_tiles = int(math.ceil(height_px/tile_size_px)) + 1 # Image height in tiles

    return (width_px, height_px), (width_tiles, height_tiles)

def download_tiles(out_folder, img_id, tiles_url, height_tiles, width_tiles):

    folder = Path(out_folder) / str(img_id)
    try:
        folder.mkdir(parents=True)
    except FileExistsError:
        pass

    print("Starting download... ")
    for j in range(height_tiles):
        for i in range(width_tiles):
            filename = folder / f"{j:04}-{i:04}.jpg"
            if not os.path.exists(filename) :
                url = tiles_url.replace("$[y]", str(j)) # Place j in URL
                url = url.replace("$[x]", str(i)) # Place i in URL
                response = urllib.request.urlopen(url)

                progress = j*width_tiles + i + 1
                print(f"[{progress/width_tiles*height_tiles}] Downloading {url} as {filename} ")

                fout = open(filename, "wb")
                fout.write(response.read())
                fout.close()

    print("Stitching... ")
    subprocess.run([
            f"{montage_command} -depth 8 -geometry 256x256+0+0 \
            -mode concatenate -tile {width_tiles}x \
            {out_folder}/{img_id}/*.jpg {out_folder}/{img_id}-giga.{output_format}"
        ], shell=True, check=True,
    )
    print("Finished!")

def main(img_name, req_level=None, out_folder=".", dry_run=False):
    """If req_level is None, the maximum resolution will be used"""

    response = urllib.request.urlopen(f"http://www.gigapan.org/gigapans/{img_name}.kml")
    img_id, tiles_url, (max_width_px, max_height_px), tile_size_px = parse_kml(response.read())

    (max_width_tiles, max_height_tiles), max_level = calculate_max_size(
            max_width_px, max_height_px, tile_size_px)

    if req_level is None:
        req_level = max_level

    (width_px, height_px), (width_tiles, height_tiles) = calculate_size(
            max_width_px, max_height_px, tile_size_px, max_level, req_level)

    tiles_url = tiles_url.replace("$[level]", str(req_level))

    print(f"""\
Provided image name: {img_name}

Gigapan image properties:
   ID: {img_id}
   Max size: {max_width_px}x{max_height_px} px
   Max number of tiles: {max_width_tiles}x{max_height_tiles} tiles = {max_width_tiles*max_height_tiles} tiles
   Max resolution level: {max_level}

Image to download:
   ID: {img_id}
   Size: {width_px}x{height_px} px
   Number of tiles: {width_tiles}x{height_tiles} tiles = {width_tiles*height_tiles} tiles
   Resolution level: {req_level}
    """)

    if not dry_run:
        download_tiles(out_folder, img_id, tiles_url, height_tiles, width_tiles)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Imprimir tablas de SQLite para DSO Guide')

    parser.add_argument('img_name', type=str,
            help='Name of image, should be obtained from the link: \
                    http://gigapan.org/gigapans/[img_name]')

    parser.add_argument('-l', '--req-level', type=int,
            help='Requested resolution level. If unset, it will download at max resolution. Try \
                    different levels with --dry-run to observe the image size')

    parser.add_argument('--dry-run', action="store_true",
            help='Fetch image metadata without downloading images. Can be used \
                        to observe the expected image size among other things.')

    parser.add_argument('-o', '--out-folder', type=str,
            help='Output folder. It will be created if it does not exist')

    args = parser.parse_args()

    main(args.img_name, args.req_level, args.out_folder, args.dry_run)
