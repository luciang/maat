"""Functions for properly handling zip files"""


import os, zipfile
from maat.storer.misc import ensure_dir_exists, humanize_bytes

def unzip_safely(archive_filename, dest_dir, max_file_size=None):
    """Run Sanity checks before unzipping a file.

    The routine checks if paths stored in a zip archive are be
    absolute or have a '..' component.

    In both cases, unzipping those files may create files outside the
    specified dest_dir. This may lead to overwritting of other
    submissions or security problems leading to priviledge escalation, etc.

    If any such file is found, unzipping is aborted (BadZipfile exception)
    """
    z = zipfile.ZipFile(archive_filename)
    try:
        if max_file_size:
            uncompressed_size = sum(e.file_size for e in z.infolist())
            if uncompressed_size > max_file_size:
                raise zipfile.BadZipfile('Size of uncompressed zip files is %s. Max allowed size is %s.' % (
                        humanize_bytes(uncompressed_size),
                        humanize_bytes(max_file_size)))

        for name in z.namelist():
            if os.path.isabs(name) or name.find('..') != -1:
                raise zipfile.BadZipfile('Absolute paths or ".." found in zipped file')
        ensure_dir_exists(dest_dir)
        z.extractall(dest_dir)
    finally:
        z.close()


def create_zip(file_handler, file_list):
    """Create a zip into the opened file_handler. The zip is comprised
    of all files specified in file_list"""
    zip_ = zipfile.ZipFile(file_handler, 'w')
    try:
        for (dest, src) in file_list:
            assert os.path.isfile(src), 'File %s is missing' % src
            zip_.write(src, dest)
    finally:
        zip_.close()

