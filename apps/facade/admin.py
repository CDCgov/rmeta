from django.contrib import admin
from .models import DataStream, Submission, Origin, SubmissionHistory


class OriginAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'application')


admin.site.register(Origin, OriginAdmin)

class SubmissionHistoryAdmin(admin.ModelAdmin):
    list_display = ('submission', 'status', 'date_created', 'date_updated')


admin.site.register(SubmissionHistory, SubmissionHistoryAdmin)


class DataStreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',) 


admin.site.register(DataStream, DataStreamAdmin)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('status', 'ori', 'cri_1', 'cri_2',
                    'dai', 'status_url')


admin.site.register(Submission, SubmissionAdmin)
