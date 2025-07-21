from django.contrib import admin
from .models import Job , Tag,Category,JobType
admin.site.register(Job)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(JobType)
