from django.contrib import admin
from maat.storer.models import Misc, HolidayInterval, UploadActiveInterval, TesterVM, Assignment


from maat.storer.models import CurrentSubmission, Submission


admin.site.register(Misc)
admin.site.register(HolidayInterval)
admin.site.register(UploadActiveInterval)
admin.site.register(TesterVM)
admin.site.register(Assignment)


admin.site.register(CurrentSubmission)
admin.site.register(Submission)

