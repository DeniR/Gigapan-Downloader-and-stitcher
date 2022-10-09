gigapan_downloader
==================

Python 3 rewrite of https://github.com/DeniR/Gigapan-Downloader-and-stitcher

Downloads gigapan pictures (tile by tile) at the resolution level specified and
then stitches the resul with Imagemagick. Should work in Windows and in
any GNU/Linux. Can resume downloads, since downloaded tiles are not reloaded.

## Installation

1. Install Python from python.org (Only necessary for Windows)
2. Install Imagemagick from
   `http://www.imagemagick.org/script/binary-releases.php#windows` (Windows). I
   recommend install `ImageMagick-*-x64-static.exe` x64 version, if you have x64
   OS. For Linux use `yum install imagemagick` or a similar command.
3. Download this script in a ZIP file using the green button on GitHub.
4. Edit script to change the path to Imagemagick (named montage) if necessary

## Running

Move to the folder and run with ``-h`` for instructions.

First it is useful to run with `--dry-run` to see the image size to download,
and then try different resolution levels with `-l` before doing the actual
download. Examples considering this image: http://gigapan.com/gigapans/130095

```
python3 ./gigapan_downloader.py -h

python3 ./gigapan_downloader.py 130095 --dry-run

python3 ./gigapan_downloader.py 130095 -l 3 --dry-run

python3 ./gigapan_downloader.py 130095 -l 3
```

### Note

Gigapan site is very slow, also this script use only one thread. If you want to
add multithreaded download - you are welcome. You can try with different
resolution levels to see the size of the image that will be downloaded and
choose the level you need, just remember to delete the downloaded tiles

### To do

- Make an error if the user downloads in a certain resolution level and then runs
    the program again in another. Already downloaded tiles will be used and it will
    be wrong

- Download in parallel

- Delete tiles and stitched lines as soon as possible to save disk, but see what
    to do to allow continuation of failed downloads
