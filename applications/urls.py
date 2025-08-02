from django.urls import path
from .views import ApplyJobView

urlpatterns = [
    path('apply/<int:job_id>/', ApplyJobView.as_view(), name='apply-job'),
]
