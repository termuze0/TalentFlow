from django.contrib import admin

# Register your models here.
from .models import CustomUser, EmployerProfile, JobSeekerProfile, UserCredential, SocialAccount, UserSession

admin.site.register(CustomUser)
admin.site.register(EmployerProfile)
admin.site.register(JobSeekerProfile)
admin.site.register(UserCredential)
admin.site.register(SocialAccount)
admin.site.register(UserSession)