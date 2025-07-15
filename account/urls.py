from django.urls import path
from .views import RegisterView,LandingPage,LoginView,ProtectedAPIView,social_login,UserhomePage

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('social-login/', social_login, name='social-login'),
    path('protected/', ProtectedAPIView.as_view(), name='protected'),
    path('', LandingPage, name='register'),
    path('home/', UserhomePage, name='UserhomePage'),
]
