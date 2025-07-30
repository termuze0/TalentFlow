from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from .models import CustomUser, UserCredential,UserSession
from .serializers import RegistrationSerializer,LoginSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated ,AllowAny
from .authentication import CustomSessionAuthentication
from django.contrib.auth.hashers import check_password
from .utils import get_client_ip
from django.conf import settings

from jobs.models import Job
import uuid
def LandingPage(request):
    return render(request, 'landing.html')

class RegisterView(APIView):
    def get(self, request):
        return render(request, 'registration/register.html')

    def post(self, request):
        if request.content_type == 'application/json':
            serializer = RegistrationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = RegistrationSerializer(data=request.POST)
            if serializer.is_valid():
                serializer.save()
                return redirect('login')  
            return render(request, 'registration/register.html', {'errors': serializer.errors, 'data': request.POST})

class LoginView(APIView):
    # authentication_classes = [CustomSessionAuthentication]
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        return render(request, 'login.html')
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = CustomUser.objects.get(email=email)
                cred = UserCredential.objects.get(user=user)
                if check_password(password, cred.password_hash):
                   
                    session_token = uuid.uuid4()
                    ip = get_client_ip(request)
                    agent = request.META.get('HTTP_USER_AGENT', '')

                    UserSession.objects.create(
                        user=user,
                        session_token=session_token,
                        ip_address=ip,
                        user_agent=agent,
                        created_at=timezone.now(),
                        expires_at=timezone.now() + timedelta(days=7),  
                        is_active=True
                    )

                    return Response({
                        "message": "Login successful",
                        "session_token": str(session_token),
                        "user": {
                            "email": user.email,
                            "fullname": user.fullname,
                            "user_type": user.user_type
                        }
                    })
                else:
                    return Response({"error": "Invalid credentials"}, status=400)
            except (CustomUser.DoesNotExist, UserCredential.DoesNotExist):
                return Response({"error": "User not found"}, status=404)
        return Response(serializer.errors, status=400)
class UserProfileView(APIView):
    

    def get(self, request):
        user = request.user
        return Response({
            "email": user.email,
            "fullname": user.fullname,
            "type": user.user_type
        })
class ProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": f"Hello {request.user.fullname}, your session is valid.",
            "user_id": request.user.id
        })


class SocialLoginView(APIView):
    def get(self, request):
        provider = request.GET.get("provider")
        code = request.GET.get("code")
        oauth_token = request.GET.get("oauth_token")
        oauth_verifier = request.GET.get("oauth_verifier")

        if provider == "google":
            if not code:
                # Step 1: Redirect to Google Auth
                auth_url = (
                    "https://accounts.google.com/o/oauth2/v2/auth"
                    "?response_type=code"
                    f"&client_id={settings.GOOGLE_CLIENT_ID}"
                    f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
                    "&scope=openid email profile"
                )
                return redirect(auth_url)
            else:
                # Step 2: Handle Google callback
                token_resp = requests.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    }
                ).json()

                access_token = token_resp.get("access_token")
                user_info = requests.get(
                    "https://www.googleapis.com/oauth2/v1/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                ).json()

                return self._create_or_login_user(request, user_info.get("email"), user_info.get("name"))

        elif provider == "twitter":
            if not code:
                # Step 1: Redirect to Twitter Auth
                auth_url = (
                    "https://twitter.com/i/oauth2/authorize"
                    "?response_type=code"
                    f"&client_id={settings.TWITTER_CLIENT_ID}"
                    f"&redirect_uri={settings.TWITTER_CALLBACK_URI}"
                    "&scope=tweet.read users.read offline.access"
                    "&state=random_state_string"
                    "&code_challenge=challenge"
                    "&code_challenge_method=plain"
                )
                return redirect(auth_url)
            else:
                # Step 2: Handle Twitter callback
                token_resp = requests.post(
            "https://api.twitter.com/2/oauth2/token",
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "client_id": settings.TWITTER_CLIENT_ID,
                    "redirect_uri": settings.TWITTER_CALLBACK_URI,
                    "code_verifier": "challenge"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ).json()

            access_token = token_resp.get("access_token")
            if not access_token:
                return Response({"error": "Failed to retrieve access token from Twitter"}, status=400)

            user_info = requests.get(
                "https://api.twitter.com/2/users/me",
                headers={"Authorization": f"Bearer {access_token}"}
            ).json()

            if "data" not in user_info:
                return Response({"error": "Failed to fetch Twitter user info"}, status=400)

            twitter_id = user_info["data"]["id"]
            name = user_info["data"]["name"]
            fake_email = f"{twitter_id}@twitter.fake"

            return self._create_or_login_user(request, fake_email, name)

            return Response({"error": "Invalid provider"}, status=400)

    def _create_or_login_user(self, request, email, name):
        user, _ = User.objects.get_or_create(email=email, defaults={"username": email.split('@')[0], "fullname": name})
        session_token = uuid.uuid4()
        ip = get_client_ip(request)
        agent = request.META.get("HTTP_USER_AGENT", "")

        UserSession.objects.create(
            user=user,
            session_token=session_token,
            ip_address=ip,
            user_agent=agent,
            created_at=timezone.now(),
            expires_at=timezone.now() + timedelta(days=7),
            is_active=True
        )

        return Response({
            "message": "Social login successful",
            "session_token": str(session_token),
            "user": {
                "email": user.email,
                "fullname": user.fullname,
                "user_type": user.user_type,
            }
        })




@api_view(['POST'])
def UserhomePage(request):
    jobs = Job.objects.all().order_by('-posted_at')
    return render(request, 'account/user_home.html',{'jobs': jobs})