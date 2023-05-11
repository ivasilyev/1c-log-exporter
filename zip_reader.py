
import tempfile
import os
from zipfile import ZipFile
from log_parser import get_file_modification_time

input_file = "rphost_1453053.zip"

from log_parser import parse_log_archive

parse_log_archive(input_file)


with ZipFile(input_file, "r") as zf:
    for info_entry in zf.infolist():
        file = info_entry.filename
        if file.endswith(".log"):
            print(file, info_entry.date_time, zf.read(file)[:200].decode("utf-8-sig"))

import datetime


info_entry.date_time

datetime.datetime(*info_entry.date_time)

imgdata = zf.read('img_01.png')



temp_dir = tempfile.TemporaryDirectory()

parse_log_archiv

