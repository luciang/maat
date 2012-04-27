from django import forms
from maat.storer.models import GradingComment

class AssignmentSubmissionForm(forms.Form):
    file = forms.FileField()


class GradingCommentForm(forms.ModelForm):
    class Meta:
        model = GradingComment
        fields = ('submission', 'filename', 'linenum', 'comment', 'grade_adjustment')
