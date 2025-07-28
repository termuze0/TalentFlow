

from django.urls import path
from . import views

urlpatterns = [
    path("jobs", views.job_list_view, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail_view, name="job_detail"),
]
