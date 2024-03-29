import os
import doctest
from traceback import format_exc
from contextlib import contextmanager

from maat.storer.models import Submission
from maat.storer.models import SubmissionError

def humanize_bytes(size, precision=1):
    """Return a humanized string representation of a number of bytes.

    Assumes `from __future__ import division`.

    >>> humanize_bytes(1)
    '1 byte'
    >>> humanize_bytes(1024)
    '1.0 kB'
    >>> humanize_bytes(1024*123)
    '123.0 kB'
    >>> humanize_bytes(1024*12342)
    '12.1 MB'
    >>> humanize_bytes(1024*12342,2)
    '12.05 MB'
    >>> humanize_bytes(1024*1234,2)
    '1.21 MB'
    >>> humanize_bytes(1024*1234*1111,2)
    '1.31 GB'
    >>> humanize_bytes(1024*1234*1111,1)
    '1.3 GB'
    """
    abbrevs = (
        (1<<50L, 'PB'),
        (1<<40L, 'TB'),
        (1<<30L, 'GB'),
        (1<<20L, 'MB'),
        (1<<10L, 'kB'),
        (1, 'bytes')
    )
    if size == 1:
        return '1 byte'
    for factor, suffix in abbrevs:
        if size >= factor:
            break
    return '%.*f %s' % (precision, 1.0 * size / factor, suffix)


def ensure_dir_exists(d):
    '''Make sure the given directory path exists'''
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except:
            # assume a race happened and someone else already created
            # the directory
            pass


def files_in_dir(top):
    '''Return a list of all files in a single directory (as relative to the directory)'''
    ret = []
    for (dirpath, dirnames, filenames) in os.walk(top):
        reldir = dirpath[len(top)+1:]
        ret.extend( [ os.path.join(reldir, f) for f in filenames ] )
    return ret


_text_characters = (b''.join(chr(i) for i in range(32, 127)) + b'\n\r\t\f\b')
def is_plain_text(s):
    '''Is the given string a binary or a plain-text?'''
    if len(s) == 0:
        # empty files are plain-text
        return True

    if len(s) > 512:
        s = s[:512] # only use the first 512 bytes to check

    if b'\x00' in s:
        # Files with null bytes are binary
        return False
    nontext = s.translate(None, _text_characters)
    if len(nontext) > 0.1 * len(s):
        # If we find a few non-text characers, pretend we didn't
        return False
    return True



def file_contents(topdir):
    '''Return a dictionary with keys files inside the topdir and
    values their contents (if plain-text)'''
    ret = { }
    for rel_name in files_in_dir(topdir):
        fname = os.path.join(topdir, rel_name)
        with open(fname, 'r') as f:
            s = f.read()
            if not is_plain_text(s):
                s = 'raw binary file (contents not displayed)'
            ret[rel_name] = s
    return ret

def save_file(sub, src_file):
    '''Save src_file to dst_fname'''
    dst_fname = sub.archive_path()
    ass = sub.assignment
    if src_file.size > ass.max_file_size:
        raise Exception('Uploaded file size=%s. Max allowed size=%s.' % (
                humanize_bytes(src_file.size),
                humanize_bytes(ass.max_file_size)))

    ensure_dir_exists(os.path.dirname(dst_fname))
    with open(dst_fname, 'wb+') as dst_file:
        for chunk in src_file.chunks():
            dst_file.write(chunk)


@contextmanager
def catch_exception_to_db(sub):
    '''Log an exception by associating it with the given submission'''
    try:
        yield
    except Exception as e:
        sub.state = Submission.STATE_ERROR
        sub.save()
        SubmissionError.objects.create(submission=sub, message=e.message, traceback=format_exc())
        # we're catching the exception, don't raise it!

