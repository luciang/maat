import os.path

from django.db import models
from django.contrib.auth.models import User



_fmt = "%a %d %b %Y %H:%M:%S" # Sat 15 Oct 2011 12:59:52

class Misc(models.Model):
    '''Some misc configurations that don't belong elsewhere. Only the
    first entry in the table is used.'''
    course_fullname = models.CharField(max_length=200,
                                       help_text='The fully-spelled course name (e.g. "Compilers 101")')
    course_nickname = models.CharField(max_length=200,
                                       help_text='A nick-name for the course (e.g. cpl-101')
    upload_root     = models.CharField(max_length=512,
                                       help_text='Directory where uploaded submissions are stored')


class HolidayInterval(models.Model):
    '''If a student submits the homework after the deadline, holidays
    are not counted as penalty-days. If you want students penalised
    during holidays too, don't add anything in this table.'''
    name = models.CharField(max_length=200, help_text='A name for this holiday')
    start = models.DateTimeField(help_text='Start of a holiday')
    stop  = models.DateTimeField(help_text='End of a holiday')

    def __unicode__(self):
        return u'%s (%s - %s)' % (self.name, self.start.strftime(_fmt), self.stop.strftime(_fmt))


class UploadActiveInterval(models.Model):
    '''Start/stop dates for when upload is active'''
    start = models.DateTimeField(help_text='Start of a period from which the students can submit homework')
    stop  = models.DateTimeField(help_text='The end of the period')
    def __unicode__(self):
        return u'Upload active between: %s - %s' % (self.start.strftime(_fmt), self.stop.strftime(_fmt))


class TesterVM(models.Model):
    '''Identification for machine that runs the tests e.g. so-lin at sanctuary.cs.pub.ro'''
    host = models.CharField(max_length=200,
                            help_text='Hostname of the tester machine (e.g. sanctuary.cs.pub.ro)')
    port = models.PositiveIntegerField(blank=True, null=True,
                               help_text='Port (e.g. 7139). Optional. Leave blank for default')
    vm_name = models.CharField(max_length=200, help_text='''Codename of the vm on the host on which to run tests.
                                                            E.g. os-lin, os-win, ai-java, etc.''')
    def __unicode__(self):
        if self.port:
            return u'%s@%s:%d' % (self.vm_name, self.host, self.port)
        else:
            return u'%s@%s' % (self.vm_name, self.host)


def upload_tests_to(instance, filename):
    return 'tests/%s_%s' % (instance.name, filename)


class Assignment(models.Model):
    '''Configuration for an assignment'''
    DEFAULT_MAX_FILE_SIZE = 1024 * 1024 # 1 MiB
    DEFAULT_MAX_POINTS = 10 # A good grade gets by default 10 points
    DEFAULT_TIMEOUT_SEC = 120

    order_number = models.PositiveIntegerField(help_text='Used for ordering. Must be unique and >= 0',
                                               unique=True)
    name = models.CharField(primary_key=True, max_length=200,
                            help_text='Keyword identifying the assignment (e.g. "backtracking-1")')
    deadline = models.DateTimeField(help_text='''Deadline for the assignment. Student can still upload
                                    homework after deadline, but a penalty is deducted (see bellow)''')
    tests = models.FileField(upload_to=upload_tests_to, max_length=512,
                                    help_text='Tests for this assignment')
    timeout_sec = models.PositiveIntegerField(default=DEFAULT_TIMEOUT_SEC,
                                              help_text='''Number of seconds of test run time after
                                              which tests are considered to never finish and execution
                                              is terminated''')
    max_points = models.DecimalField(decimal_places=3, max_digits=10, default=DEFAULT_MAX_POINTS,
                                     help_text='Number of points (grade) for a perfect submission')
    max_file_size = models.IntegerField(default=DEFAULT_MAX_FILE_SIZE,
                                        help_text='Maximum size of files uploaded by the students')
    penalty = models.CharField(max_length=200, help_text='''Penalty formula for late submissions.
                               Must be of this form <b>'[(p1, n1), (p2,n2), ...]'</b>. <br>
                               Meaning: first n1 days subtract p1 points for each day,
                                        next <b>n2</b> days subtract p2 points for each day, etc.''')
    test_vms = models.ManyToManyField(TesterVM, help_text='TestVMs to use for this assignment')

    def __unicode__(self):
        return self.name

    class Meta:
        # when retrieving assignments we need to make sure to get them
        # ordered by their number
        ordering = ['order_number']



class Submission(models.Model):
    '''Table of all submissions'''
    STATE_NEW      = 'new'
    STATE_ERROR    = 'error'
    STATE_QUEUED   = 'queued'
    STATE_CANCELED = 'canceled'
    STATE_TESTED   = 'tested'
    STATE_GRADED   = 'graded'
    STATE_COPIED   = 'copied'

    user        = models.ForeignKey(User, related_name='submissions', help_text='User who submitted this')
    assignment  = models.ForeignKey(Assignment, related_name='submissions',
                                    help_text='For which assignment is this submission')
    upload_time = models.DateTimeField(help_text='Date+time of upload')
    state       = models.CharField(max_length=20, help_text='Current state (new, queued, canceled, etc.)')
    message     = models.CharField(default=None, max_length=512, blank=True,
                                   help_text='Extended error messages')
    grade       = models.DecimalField(decimal_places=3, max_digits=10, blank=True,
                                      null=True, help_text='The grade of the submission')
    def __unicode__(self):
        return u'Submission(user=%s,assignment=%s,state=%s,upload-time=%s)' % (
            self.user.username, self.assignment.name,
            self.detailed_desc(), self.upload_time.strftime(_fmt))

    def short_desc(self):
        if self.state == Submission.STATE_GRADED:
            return unicode(self.grade)
        else:
            return self.state

    def detailed_desc(self):
        if self.state == Submission.STATE_GRADED:
            return unicode(self.grade)
        elif len(self.message) == 0:
            return self.state
        else:
            return u'%s: %s' % (self.state, self.message)

    def root_path(self):
        return 'submissions/%s/%s/%d' % (self.user.username, self.assignment.name, self.id)

    def archive_path(self):
        return os.path.join(self.root_path(), 'archive.zip')

    def extracted_path(self):
        return os.path.join(self.root_path(), 'extracted')


class CurrentSubmission(models.Model):
    '''The user can upload the same homework multiple times. Only a
    single submission entry will be part of this table (normally the
    last one). In case the student wants to cancel a submission he can
    set the current submission to be a previous one.'''
    user       = models.ForeignKey(User, related_name='current_submission',
                                   help_text='User who submitted this')
    assignment = models.ForeignKey(Assignment, related_name='current_submission',
                                   help_text='For which assignment is this submission')
    submission = models.ForeignKey(Submission, related_name='current_submission',
                                   help_text='Submission for which this grade is given')
    class Meta:
        unique_together = ('user', 'assignment')
    def __unicode__(self):
        return u'Current' + unicode(self.submission)



#TODO: once a homework is graded, it no longer can be uploaded?
#TODO: student should be able to resubmit homework for evaluation
#TODO: if student submits the same homework multiple times, it shouldn't be reevaluated (md5?)
#TODO: if student submits a revised homework, the old one should not be evaluated (if possible)



class GradingComment(models.Model):
    '''All comments added by teachers while grading the homework'''
    submission       = models.ForeignKey(Submission, related_name='grading_comments',
                                         help_text='Submission for which this grade is given')
    file_name        = models.CharField(max_length=200, help_text='File being graded')
    line             = models.PositiveIntegerField(help_text='Line number where comment should be included')
    comment          = models.CharField(max_length=200, help_text='Text of the comment')
    grade_adjustment = models.DecimalField(decimal_places=3, max_digits=10,
                                           help_text='Penalty/Bonus associated with comment')

