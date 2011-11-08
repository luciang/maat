# Create your views here.

import datetime
from collections import OrderedDict

from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.db import transaction

from maat.storer.models import Assignment, CurrentSubmission, Submission, SubmissionError
from maat.storer.forms import AssignmentSubmissionForm
from maat.storer.shortcuts import render_to, update_or_create
from maat.storer.misc import save_file, file_contents, catch_exception_to_db
from maat.storer.tasks import delayed_submission_processing


@render_to('home.html')
def home(request):
    assignments = Assignment.objects.order_by('order_number').values('name')
    ass_idx = { a['name']: idx for idx, a in enumerate(assignments) }
    csubs = CurrentSubmission.objects.select_related().order_by('user__username', 'assignment').all()

    grades_dict = { }
    for csub in csubs:
        if not csub.user.username in grades_dict:
            grades_dict[csub.user.username] = { }
        grades_dict[csub.user.username][csub.assignment.name] = csub.submission

    grades = []
    for username, ass_dict in grades_dict.items():
        row = [ None ] * (len(assignments) + 1)
        row[0] = username
        for ass_name, sub in ass_dict.items():
            row[ass_idx[ass_name] + 1] = sub.short_desc()
        grades.append(row)
    return { 'grades' : grades, 'assignments' : assignments }


@render_to('assignment_form.html')
@transaction.commit_on_success
@login_required
def assignment_form(request, ass_name):
    ass = get_object_or_404(Assignment, name=ass_name)
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            try:
                sub = Submission.objects.create(user=request.user, assignment=ass,
                                                upload_time=datetime.datetime.now(),
                                                state=Submission.STATE_NEW, grade=None)
                update_or_create(CurrentSubmission,
                                 { 'user': request.user, 'assignment': ass },
                                 { 'submission': sub })
            except:
                transaction.rollback()
                raise
            # need to commit manually to prevent race with celery
            # see http://ask.github.com/celery/userguide/tasks.html#database-transactions
            transaction.commit()

            with catch_exception_to_db(sub):
                save_file(sub, uploaded_file)
                delayed_submission_processing.delay(sub.id)

            # response: redirect relative to the current assignment to
            # the page of the user: assignment/$(assignment-code)/$(user-name)
            return HttpResponseRedirect(request.user.username)

    form = AssignmentSubmissionForm()
    c = { 'assignment' : ass, 'form' : form }
    c.update(csrf(request))
    transaction.commit()
    return c


@render_to('current_submission.html')
@login_required
def submission(request, ass_name, username, subm_id):
    ass = get_object_or_404(Assignment, name=ass_name)
    sub = get_object_or_404(Submission, pk=subm_id)
    errors = SubmissionError.objects.filter(submission=sub)
    return {'assignment' : ass, 'submission': sub, 'errors': errors }


@render_to('current_submission.html')
@login_required
def current_submission(request, ass_name, username):
    ass = get_object_or_404(Assignment, name=ass_name)
    user = get_object_or_404(User, username=username)
    csub = get_object_or_404(CurrentSubmission, user=user, assignment=ass)
    sub = csub.submission
    errors = SubmissionError.objects.filter(submission=sub)
    files = file_contents(sub.extracted_path())
    return {'assignment' : ass, 'submission': sub, 'errors': errors, 'files': files }

