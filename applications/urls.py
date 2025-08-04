from django.urls import path
from .views import ApplyJobView, MyApplicationsView

urlpatterns = [
    path('jobs/<int:job_id>/apply/', ApplyJobView.as_view(), name='apply-job'),
    path('my-applications/', MyApplicationsView.as_view(), name='my_applications'),
]
