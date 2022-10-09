import pytest

import gigapan_downloader
from pathlib import Path
import re


@pytest.mark.parametrize("img_name", ["130095", "0d54f8d3323a60308eb2ff9831edfe4a"])
def test_integration(mocker, img_name):


    def urllopen(url):
        response = mocker.Mock()
        if url == f"http://www.gigapan.org/gigapans/{img_name}.kml":
            response.read.return_value = Path(".", "test_data", f"{img_name}.kml").read_text()

        else:
            assert re.fullmatch(r"http://gigapan.com/get_ge_tile/\d+/\d+/\d+/\d+.*", url)
            response.read.return_value = Path(".", "test_data", "sample_tile.jpg").read_bytes()

        return response

    out_folder = "./test_results/"

    urllopen_mock = mocker.patch("urllib.request.urlopen", side_effect=urllopen)
    gigapan_downloader.main(img_name, req_level=2, out_folder=out_folder)

    # assert Path(".", "downloads", );
