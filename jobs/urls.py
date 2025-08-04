

from django.urls import path
from . import views
from .views import SavedJobView, SaveJobView, CheckSavedStatusView
urlpatterns = [
    path("jobs", views.job_list_view, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail_view, name="job_detail"),
    path('jobs/saved/', SavedJobView.as_view(), name='saved-jobs'),
    path('jobs/<int:job_id>/save/', SaveJobView.as_view(), name='save-job'),
    path('jobs/saved-jobs/<int:job_id>/status/', CheckSavedStatusView.as_view(), name='check_saved_status'),
]
