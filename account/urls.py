from django.urls import path
from .views import RegisterView,LandingPage

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', LandingPage, name='register'),
]
