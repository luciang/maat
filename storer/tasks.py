from celery.task import task

from maat.storer.models import Submission
from maat.storer.ziputil import unzip_safely
from maat.storer.misc import save_submission_and_log_exception


@task(ignore_result=True)
def delayed_submission_processing(sub_id):
    _unzip_submission.delay(sub_id)


@task(ignore_result=True)
@save_submission_and_log_exception
def _unzip_submission(sub):
    dest_dir = sub.extracted_path()
    zip_file = sub.archive_path()
    unzip_safely(zip_file, dest_dir, sub.assignment.max_file_size)
    _send_to_evaluation.delay(sub_id)
    sub.message = ''
    sub.state = Submission.STATE_QUEUED



@task(ignore_result=True)
def _send_to_evaluation(sub_id):
    sub = Submission.objects.get(pk=sub_id)
    pass
