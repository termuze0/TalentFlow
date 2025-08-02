from django.urls import path
from .views import ApplyJobView, MyApplicationsView

urlpatterns = [
    path('apply/<int:job_id>/', ApplyJobView.as_view(), name='apply-job'),
    path('my-applications/', MyApplicationsView.as_view(), name='my_applications'),
]
