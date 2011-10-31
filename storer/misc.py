import os
import doctest

from maat.storer.models import Submission

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


def save_submission_and_log_exception(fun):
    '''Decorator that saves the error encountered while processing a
    submission insiged Submission.message and sets it's state to
    STATE_ERROR while making sure to save the submission object before
    returning.
    
    It looks for two keyword arguments to get the submission:
     * sub - a Submission instance
     * sub_id - the Submission.id of an instance.

    NOTE:
     * this decorator will replace sub_id with it's corresponding
       'sub' instance in **kwargs
     * both 'sub' and 'sub_id' must be sent as keyword arguments to
       the decorated functions.
    '''
    def wrapper(*args, **kwargs):
        print args
        print kwargs
        if 'sub' in kwargs:
            sub = kwargs['sub']
        else:
            sub = Submission.objects.get(pk=kwargs['sub_id'])
            del kwargs['sub_id']
            kwargs['sub'] = sub
        try:
            fun(*args, **kwargs)
        except Exception as e:
            sub.state = Submission.STATE_ERROR
            sub.message = e.message
        finally:
            sub.save()
    return wrapper
