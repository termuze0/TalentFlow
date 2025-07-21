

from django.urls import path
from . import views

urlpatterns = [
    path("", views.job_list_view, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail_view, name="job_detail"),
]
