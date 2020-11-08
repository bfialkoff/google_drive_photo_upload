import io
import re
from pathlib import Path

from PIL import Image


class FileHandler:

    def __init__(self, src_file):
        self.file_name = src_file.name

        # decode the capture year and month for archiving
        self.year, self.month = self.get_capture_date(self.file_name)

        # for some reason we need rewrite the src image

        # here we capture the bytes of the image
        self.src_bytes_obj = self.get_src_bytes(src_file)

        # here we write it back to the disk
        self.write_temp_file()

    def get_src_bytes(self, src_file):
        src_img_fp = src_file.open('rb')
        src_bytes_obj = io.BytesIO(src_img_fp.read())
        src_img_fp.close()
        return src_bytes_obj

    def write_temp_file(self):
        dst_img_fp = Image.open(self.src_bytes_obj)
        dst_img_fp.save(self.file_name)
        dst_img_fp.close()

    def cleanup(self):
        # this is for deleting the temporary file we created
        Path(self.file_name).unlink()

    @classmethod
    def get_capture_date(cls, file_name):
        # a 8 character substring of digits beginning with 20, will yield the capture date
        res = re.search("(20[0-9]{6})", file_name)[0]
        year = res[:4]
        month = f'{res[4:6]}-{year[2:]}'
        return year, month
