from django.db import models


class Misc(models.Model):
    '''Some misc configurations that don't belong elsewhere. Only the
    first entry in the table is used.'''
    course_fullname = models.CharField(max_length=200,  help_text='The fully-spelled course name (e.g. "Compilers 101")')
    course_nickname = models.CharField(max_length=200,  help_text='A nick-name for the course (e.g. cpl-101')
    upload_root     = models.CharField(max_length=512, help_text='Directory where uploaded submissions are stored')


class Holidays(models.Model):
    '''If a student submits the homework after the deadline, holidays
    are not counted as penalty-days. If you want students penalised
    during holidays too, don't add anything in this table.'''
    start = models.DateTimeField(help_text='Start of a holiday')
    stop  = models.DateTimeField(help_text='End of a holiday')


class UploadActivity(models.Model):
    '''Start/stop dates for when upload is active'''
    start = models.DateTimeField(help_text='Start of a period from which the students can submit homework')
    stop  = models.DateTimeField(help_text='The end of the period')


class TesterVM(models.Model):
    '''Identification for machine that runs the tests e.g. so-lin at sanctuary.cs.pub.ro'''
    host = models.CharField(max_length=200, help_text='Hostname of the tester machine (e.g. sanctuary.cs.pub.ro)')
    port = models.IntegerField(blank=True, null=True, help_text='Port for the tester machine (e.g. 7139). Optional. Leave blank for default')
    name = models.CharField(max_length=200, help_text='ID of the machine on the host (e.g. so-lin or so-win)')


class Assignment(models.Model):
    '''Configuration for an assignment'''
    order_number = models.IntegerField(help_text='the number of this assignment (used to order assignments)',
                                       unique=True)
    name         = models.CharField(max_length=200, help_text='Keyword identifying the assignment (e.g. "backtracking-1")')
    deadline     = models.DateTimeField(help_text='Date+time after which the grade is lowered')
    tests        = models.CharField(max_length=512, help_text='A file that contains the tests for this homework')
    timeout_sec  = models.IntegerField(help_text='''Nr. of seconds of test run time after
                                                    which tests are considered to never
                                                    finish and execution is terminated)''')
    max_points   = models.DecimalField(decimal_places=3, max_digits=10,
                                       help_text='Nr points student gets if submission works OK')
    penalty      = models.CharField(max_length=200, help_text='''Penalty points for each day after deadline.
                                                                 Must be of this form '[(p1, n1), (p2,n2), ...]'.
                                                                 Meaning: first n1 days subtract p1 for each day,
                                                                           next n2 days subtract p2 for each day, etc.''')
    test_vms     = models.ManyToManyField(TesterVM, help_text='TestVMs to use for this assignment')

    class Meta:
        # when retrieving assignments we need to make sure to get them
        # ordered by their number
        ordering = ['order_number']



class Submission(models.Model):
    '''Table of all submissions'''
    username    = models.CharField(max_length=200, help_text='The name of the user that created this submission')
    assignment  = models.ForeignKey(Assignment, related_name='submissions', help_text='For which assignment is this submission')
    upload_time = models.DateTimeField(help_text='Date+time of upload')
    upload_file = models.CharField(max_length=512, help_text='The path to the file uploaded by the student')
    evaluated   = models.BooleanField(help_text='Have the evaluation results arrived?')
    grade       = models.DecimalField(decimal_places=3, max_digits=10, blank=True,
                                      null=True, help_text='The grade of the submission')


class CurrentSubmission(models.Model):
    '''The user can upload the same homework multiple times. Only a
    single submission entry will be part of this table (normally the
    last one). In case the student wants to cancel a submission he can
    set the current submission to be a previous one.'''
    username   = models.CharField(max_length=200, help_text='The name of the user that created this submission')
    assignment = models.ForeignKey(Assignment, related_name='current_submissions', help_text='For which assignment is this submission')
    submission = models.ForeignKey(Submission, related_name='current_submissions', help_text='Submission for which this grade is given')
    class Meta:
        unique_together = (('username', 'assignment'),)



#TODO: once a homework is graded, it no longer can be uploaded?
#TODO: student should be able to resubmit homework for evaluation
#TODO: if student submits the same homework multiple times, it shouldn't be reevaluated (md5?)
#TODO: if student submits a revised homework, the old one should not be evaluated (if possible)



class GradingComments(models.Model):
    '''All comments added by teachers while grading the homework'''
    submission       = models.ForeignKey(Submission, related_name='grading_comments', help_text='Submission for which this grade is given')
    file_name        = models.CharField(max_length=200, help_text='File being graded')
    line             = models.IntegerField(help_text='Line number where comment should be included')
    comment          = models.CharField(max_length=200, help_text='Text of the comment')
    grade_adjustment = models.DecimalField(decimal_places=3, max_digits=10,
                                           help_text='Penalty/Bonus associated with comment')

