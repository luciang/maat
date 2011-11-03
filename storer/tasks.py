from celery.task import task

from maat.storer.models import Submission
from maat.storer.ziputil import unzip_safely
from maat.storer.misc import catch_exception_to_db


@task(ignore_result=True)
def delayed_submission_processing(sub_id):
    _unzip_submission.delay(sub_id)


@task(ignore_result=True)
def _unzip_submission(sub_id):
    sub = Submission.objects.get(pk=sub_id)
    with catch_exception_to_db(sub):
        dest_dir = sub.extracted_path()
        zip_file = sub.archive_path()
        unzip_safely(zip_file, dest_dir, sub.assignment.max_file_size)

        _create_syntax_highlighting.delay(sub_id)
        _send_to_evaluation.delay(sub_id)


@task(ignore_result=True)
def _send_to_evaluation(sub_id):
    sub = Submission.objects.get(pk=sub_id)
    print('Sending submission %d %s to evaluation ******* TODO implement ^^^^^^^' % (sub_id, sub))


@task(ignore_result=True)
def _create_syntax_highlighting(sub_id):
    sub = Submission.objects.get(pk=sub_id)
    print('Creating pygments for %d %s  ******* TODO implement ^^^^^^^' % (sub_id, sub))
