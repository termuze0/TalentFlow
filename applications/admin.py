from django.contrib import admin

from .models import  JobApplication, ApplicationStatus
admin.site.register(JobApplication)
admin.site.register(ApplicationStatus)