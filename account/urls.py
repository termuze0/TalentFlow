from django.urls import path
from .views import RegisterView,LandingPage,LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', LandingPage, name='register'),
]
