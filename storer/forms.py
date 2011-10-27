from django import forms

class AssignmentSubmissionForm(forms.Form):
    file = forms.FileField()

