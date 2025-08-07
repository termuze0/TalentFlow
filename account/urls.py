from django.urls import path
from .views import RegisterView,LandingPage,LoginView,ProtectedAPIView,UserhomePage,SocialLoginView,UserInfoView,UserProfile

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    path('protected/', ProtectedAPIView.as_view(), name='protected'),
    path('', LandingPage, name='register'),
    path('home/', UserhomePage, name='home'),
    path("social-login/", SocialLoginView.as_view(), name="social_login"),
    path("oauth2/callback/google/", SocialLoginView.as_view()),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('user/profile/', UserProfile.as_view(), name='user_profile'),


]
