# Create your views here.

from collections import OrderedDict

from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from django.db import transaction

from maat.storer.models import Assignment, CurrentSubmission, Submission
from maat.storer.forms import AssignmentSubmissionForm
from maat.storer.shortcuts import render_to, update_or_create


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
            row[ass_idx[ass_name] + 1] = sub.state()
        grades.append(row)
    return { 'grades' : grades, 'assignments' : assignments }


@login_required
def assignment_form(request, ass_name):
    ass = get_object_or_404(Assignment, name=ass_name)
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            sub = Submission.objects.create(user=request.user, assignment=ass,
                                            upload_file=cd['file'],
                                            evaluated=False, grade=None)
            update_or_create(CurrentSubmission,
                             { 'user': request.user, 'assignment': ass },
                             { 'submission': sub })
            # response: redirect relative to the current assignment to
            # the page of the user: assignment/$(assignment-code)/$(user-name)
            return HttpResponseRedirect(request.user.username)

    form = AssignmentSubmissionForm()
    c = { 'assignment' : ass, 'form' : form }
    c.update(csrf(request))
    return render_to_response('assignment_form.html', c)


@render_to('current_submission.html')
@login_required
def submission(request, ass_name, username, subm_id):
    ass = get_object_or_404(Assignment, name=ass_name)
    sub = get_object_or_404(Submission, pk=subm_id)
    return {'assignment' : ass, 'submission': sub }


@render_to('current_submission.html')
@login_required
def current_submission(request, ass_name, username):
    ass = get_object_or_404(Assignment, name=ass_name)
    user = get_object_or_404(User, username=username)
    csub = get_object_or_404(CurrentSubmission, user=user, assignment=ass)
    sub = csub.submission
    return {'assignment' : ass, 'submission': sub }

