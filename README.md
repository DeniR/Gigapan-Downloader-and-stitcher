# Gigapan Downloader and Stitcher

## Download and assemble Gigapan panoramas into a single JPEG

This cross-platform Python 3 script downloads Gigapan images at the resolution you specify, then stitches the tiles together using ImageMagick into one large JPG image.

- ✅ Works on Windows and Linux  
- 🔁 Supports resume: already-downloaded tiles will be skipped  
- 🧱 Only missing tiles are fetched — ideal for slow connections  
- 🖼 Outputs a single trimmed JPEG file

---

## How to Use

1. **Install Python 3.x**  
   - [Download from python.org](https://www.python.org/downloads/) for Windows  
   - On Linux: use your package manager (e.g., `sudo apt install python3` or `sudo yum install python3`)

2. **Install ImageMagick**  
   - [Download for Windows](https://imagemagick.org/script/download.php#windows)  
     Recommended: `ImageMagick-*-x64-static.exe` if you have a 64-bit OS  
   - On Linux: `sudo apt install imagemagick` or `sudo yum install imagemagick`

3. **Download the script**  
   Save this file:  
   [`gigapanDownloader.py`](https://raw.github.com/DeniR/Gigapan-Downloader-and-stitcher/master/gigapanDownloader.py)

4. **Set the path to ImageMagick**  
   Edit the script to reflect your OS:

   ```python
   imagemagick = "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"  # Windows
   imagemagick = "/usr/bin/magick"  # Linux
5. Run the script
   ```bash
   python gigapanDownloader.py <imageid> <level>

  * `<imageid>`: the numeric ID from the Gigapan URL 
 * `<level>`: resolution level to download (use 0 for highest resolution)

## Example

Gigapan URL:  
https://www.gigapan.com/gigapans/130095  
Here, the image ID is `130095`.

```bash
python gigapanDownloader.py 130095 5
```
This will:
* Download tiles for level 5 into the folder `/130095`
* Stitch them into a single image file: `130095.jpg`
   
To download the highest resolution, use:

```bash
python gigapanDownloader.py 130095 0
```

## Notes
* Gigapan servers are often slow — be patient.
* This script uses a single-threaded downloader.
* Already-downloaded tiles will not be re-downloaded.
* To try a different level, delete the old tiles first.
* Only JPG output is supported by this version.
