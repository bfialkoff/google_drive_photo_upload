import io
import re
from pathlib import Path

from PIL import Image
from PIL import ExifTags

ExifTags.TAGS


class FileHandler:

    def __init__(self, src_file):
        self.file_name = src_file.parent.joinpath(src_file.name)
        self.name = self.file_name.name
        # decode the capture year and month for archiving
        self.year, self.month = self.get_capture_date(src_file)

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
    def _parse_from_filename(cls, file_name):
        year, month = None, None
        # a 8 character substring of digits beginning with 20, will yield the capture date
        res_1 = re.search("(20[0-9]{6})", file_name)

        # date in the form yyyy-mm-dd
        res_2 = re.search("(20[0-9]{2}-[0-9]{2}-[0-9]{2})", file_name)
        if res_1 is not None:
            res = res_1[0]
            year = res[:4]
            month = f'{res[4:6]}-{year[2:]}'
        elif res_2 is not None:
            res = res_2[0]
            year = res[:4]
            month = f'{res[5:7]}-{year[2:]}'
        return year, month

    @classmethod
    def get_capture_date(cls, src_file):
        file_name = src_file.name
        year, month = cls._parse_from_filename(file_name)
        if year is None:
            # todo work with exif data
            year, month = '0000', '00-00'
            print(f"couldn't determine date, using {year}, and {month} instead")
        return year, month
