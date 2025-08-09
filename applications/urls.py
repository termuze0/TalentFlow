from django.urls import path
from .views import ApplyJobView, MyApplicationsView,ResumeUploadView

urlpatterns = [
    path('jobs/<int:job_id>/apply/', ApplyJobView.as_view(), name='apply-job'),
    path('my-applications/', MyApplicationsView.as_view(), name='my_applications'),
    path('my_resume/', ResumeUploadView.as_view(), name='my_resume'),
    
]
