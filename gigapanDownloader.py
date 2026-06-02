# usage: python gigapanDownloader.py <photoid> <level>
# example: python gigapanDownloader.py 231697 0
# level 0 = highest resolution

import sys
import os
import math
import subprocess
from xml.dom.minidom import parseString
from urllib.request import urlopen


# Path to ImageMagick's montage command
if os.name == "nt":
    imagemagick = "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"
else:
    imagemagick = "/usr/bin/magick"

# Helper: extract text from DOM
def getText(nodelist):
    return ''.join([node.data for node in nodelist if node.nodeType == node.TEXT_NODE])

# Helper: find element value by name
def find_element_value(e, name):
    nodes = [e]
    while nodes:
        node = nodes.pop()
        if node.nodeType == node.ELEMENT_NODE and node.localName == name:
            return getText(node.childNodes)
        else:
            nodes.extend(node.childNodes)
    return None

# Main
if len(sys.argv) != 3:
    print("Usage: python gigapanDownloader.py <photoid> <level>")
    sys.exit(1)

photo_id = int(sys.argv[1])
level = int(sys.argv[2])
base_url = "http://www.gigapan.org"

# Create output folder
output_dir = str(photo_id)
os.makedirs(output_dir, exist_ok=True)

# Download and parse KML
kml_url = f"{base_url}/gigapans/{photo_id}.kml"
with urlopen(kml_url) as h:
    photo_kml = h.read().decode("utf-8")
dom = parseString(photo_kml)

# Read image info
maxheight = int(find_element_value(dom.documentElement, "maxHeight"))
maxwidth = int(find_element_value(dom.documentElement, "maxWidth"))
tile_size = int(find_element_value(dom.documentElement, "tileSize"))

# Compute max level
max_tiles_x = math.ceil(maxwidth / tile_size)
max_tiles_y = math.ceil(maxheight / tile_size)
maxlevel = int(math.ceil(math.log(max(max_tiles_x, max_tiles_y), 2)))

if level == 0:
    level = maxlevel

scale = 2 ** (maxlevel - level)
width = int(maxwidth / scale)
height = int(maxheight / scale)
wt = int(math.ceil(width / tile_size))
ht = int(math.ceil(height / tile_size))

# Report
print('+----------------------------')
print(f'| Max size: {maxwidth}x{maxheight}px')
print(f'| Max level: {maxlevel}')
print(f'| Tile size: {tile_size}')
print('+----------------------------')
print(f'| Downloading Level {level}')
print(f'| Target size: {width}x{height}px')
print(f'| Grid: {wt} x {ht} tiles = {wt * ht} total')
print('+----------------------------')
print()

# Download tiles
errors = 0
for j in range(ht):
    for i in range(wt):
        filename = f"{j:04d}-{i:04d}.jpg"
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            url = f"{base_url}/get_ge_tile/{photo_id}/{level}/{j}/{i}"
            print(f"Downloading ({j},{i}) → {filename}")
            try:
                with urlopen(url) as h:
                    with open(path, "wb") as fout:
                        fout.write(h.read())
            except Exception as e:
                print(f"❌ Failed to download tile {j},{i}: {e}")
                errors += 1

# Stitch tiles with ImageMagick
if errors == 0:
    print("✅ Download complete. Starting stitch...")
    for j in range(ht):
        lineNo = f"{j:04d}"
        print('Creating line', lineNo)
        tile_files = [f"{photo_id}/{lineNo}-{i:04d}.jpg" for i in range(wt)]
        subprocess.call([
            imagemagick, "montage",
            "-depth", "8",
            "-geometry", "256x256+0+0",
            "-tile", f"{wt}x"
        ] + tile_files + [f"{photo_id}/line-{lineNo}.jpg"])

    # Combine all rows
    line_files = [f"{photo_id}/line-{j:04d}.jpg" for j in range(ht)]
    final_output = f"{photo_id}.jpg"
    print(f"Combining all rows into {photo_id}.jpg...")
    subprocess.call([
        imagemagick, "montage",
        "-geometry", f"{wt * 256}x256+0+0",
        "-tile", f"x{ht}"
    ] + line_files + [
        f"{photo_id}-stitched.jpg"
    ])

    # Trim the black edges
    subprocess.call([
        imagemagick,
        f"{photo_id}-stitched.jpg",
        "-trim",
        "+repage",  # resets the virtual canvas size
        f"{photo_id}.jpg"
    ])

    # Cleanup intermediate file
    os.remove(f"{photo_id}-stitched.jpg")

    print("✅ Done.")
else:
    print(f"⚠️ {errors} tile(s) failed to download. Retry recommended.")
