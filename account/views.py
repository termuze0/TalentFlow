from rest_framework.views import APIView
from django.views import View
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
import requests
import secrets
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import  method_decorator
from jobs.models import Job, Category
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

from django.shortcuts import redirect

class LoginView(APIView):
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
                    session_token = str(uuid.uuid4())
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

                    
                    request.session['session_token'] = session_token
                    request.session['email'] = user.email
                    request.session['fullname'] = user.fullname
                    request.session['user_type'] = user.user_type

                    return redirect('/home/')  
                else:
                    return render(request, 'login.html', {'error': 'Invalid credentials'})

            except (CustomUser.DoesNotExist, UserCredential.DoesNotExist):
                return render(request, 'login.html', {'error': 'User not found'})

        return render(request, 'login.html', {'errors': serializer.errors})

class LogoutView(APIView):
    def post(self, request):
        
        session_token = request.session.get('session_token')

        if session_token:
            
            UserSession.objects.filter(session_token=session_token, is_active=True).update(
                is_active=False,
                expires_at=timezone.now()
            )

        
        request.session.flush()  

        return redirect('/login/')
    
    def get(self, request):
        
        return self.post(request)
class UserInfoView(APIView):
    def get(self, request):
        session_token =request.META.get("HTTP_SESSION_TOKEN")

        if not session_token:
            return Response({'error': 'Missing session token'}, status=401)

        try:
            session = UserSession.objects.get(session_token=session_token, is_active=True)
            if session.expires_at < timezone.now():
                return Response({'error': 'Session expired'}, status=401)

            user = session.user
            return Response({
                'email': user.email,
                'fullname': user.fullname,
                'user_type': user.user_type
            })
        except UserSession.DoesNotExist:
            return Response({'error': 'Invalid session'}, status=401)


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
                auth_url = (
                    "https://accounts.google.com/o/oauth2/v2/auth"
                    "?response_type=code"
                    f"&client_id={settings.GOOGLE_CLIENT_ID}"
                    f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
                    "&scope=openid email profile"
                )
                return redirect(auth_url)
            else:
                
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
                
                code_verifier = secrets.token_urlsafe(64)
                request.session["code_verifier"] = code_verifier
                code_challenge = code_verifier  

                auth_url = (
                    "https://twitter.com/i/oauth2/authorize"
                    "?response_type=code"
                    f"&client_id={settings.TWITTER_CLIENT_ID}"
                    f"&redirect_uri={settings.TWITTER_CALLBACK_URI}"
                    "&scope=tweet.read users.read offline.access"
                    "&state=xyz123"  
                    f"&code_challenge={code_challenge}"
                    "&code_challenge_method=plain"
                )
                return redirect(auth_url)
            else:
                
                code_verifier = request.session.get("code_verifier")
                if not code_verifier:
                    return Response({"error": "Missing code_verifier"}, status=400)

                token_resp = requests.post(
                    "https://api.twitter.com/2/oauth2/token",
                    data={
                        "code": code,
                        "grant_type": "authorization_code",
                        "client_id": settings.TWITTER_CLIENT_ID,
                        "redirect_uri": settings.TWITTER_CALLBACK_URI,
                        "code_verifier": code_verifier,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if token_resp.status_code != 200:
                    return Response({"error": "Failed to retrieve access token from Twitter"}, status=400)

                token_data = token_resp.json()
                access_token = token_data.get("access_token")
                if not access_token:
                    return Response({"error": "No access token received"}, status=400)

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
        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "fullname": name,
                "user_type": "JOB_SEEKER",  
                "phone": "",
                "is_active": True
            }
        )

        if not user.is_active:
            user.is_active = True
            user.save()

        session_token = str(uuid.uuid4())
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
        request.session['session_token'] = session_token
        request.session['email'] = user.email
        request.session['fullname'] = user.fullname
        request.session['user_type'] = user.user_type

      
        return redirect('/home/')

@method_decorator(csrf_exempt, name='dispatch')
class UserProfile(View):
    def get_user_from_token(self, request):
        session_token = request.headers.get('Session-Token')
        if not session_token:
            return None, JsonResponse({'error': 'Missing session token'}, status=401)

        try:
            session = UserSession.objects.get(session_token=session_token, is_active=True)
            if session.expires_at < timezone.now():
                return None, JsonResponse({'error': 'Session expired'}, status=401)
            return session.user, None
        except UserSession.DoesNotExist:
            return None, JsonResponse({'error': 'Invalid session token'}, status=401)
    def get(self,request):
        return render(request , 'account/user_profile.html')
    def post(self, request):
        user, error = self.get_user_from_token(request)
        if error:
            return error

        profile_data = {
            'email': user.email,
            'fullname': user.fullname,
            'user_type': user.user_type,
            'phone': user.phone,
            'joined': user.joined.strftime('%Y-%m-%d'),
        }

        if user.is_job_seeker():
            try:
                profile = user.jobseeker_profile
                profile_data.update({
                    'bio': profile.bio,
                    'skills': profile.skills,
                    'education': profile.education,
                    'experience': profile.experience,
                    'portfolio_url': profile.portfolio_url,
                    'linkedin_url': profile.linkedin_url,
                    'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
                    'resume': profile.resume.url if profile.resume else None,
                })
            except JobSeekerProfile.DoesNotExist:
                profile_data['profile_error'] = 'Job seeker profile not found.'

        elif user.is_employer():
            try:
                profile = user.employer_profile
                profile_data.update({
                    'company_website': profile.company_website,
                    'company_description': profile.company_description,
                    'company_logo': profile.company_logo.url if profile.company_logo else None,
                    'address': profile.address,
                    'industry': profile.industry,
                    'founded_year': profile.founded_year,
                    'social_media': profile.social_media or {},
                })
            except EmployerProfile.DoesNotExist:
                profile_data['profile_error'] = 'Employer profile not found.'

        return JsonResponse({'user_profile': profile_data})

    def put(self, request):
        user, error = self.get_user_from_token(request)
        if error:
            return error

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        
        for field in ['fullname', 'phone']:
            if field in data:
                setattr(user, field, data[field])
        user.save()

        if user.is_job_seeker():
            profile, _ = JobSeekerProfile.objects.get_or_create(user=user)
            for field in ['bio', 'skills', 'education', 'experience', 'portfolio_url', 'linkedin_url']:
                if field in data:
                    setattr(profile, field, data[field])
            profile.save()

        elif user.is_employer():
            profile, _ = EmployerProfile.objects.get_or_create(user=user)
            for field in ['company_website', 'company_description', 'address', 'industry', 'founded_year', 'social_media']:
                if field in data:
                    setattr(profile, field, data[field])
            profile.save()

        return JsonResponse({'message': 'Profile updated successfully'})

@api_view(['GET'])
def UserhomePage(request):
    

    jobs = Job.objects.select_related('employer', 'category').order_by('-posted_at')[:50]
    categories = Category.objects.all()
    locations = Job.objects.values_list('location', flat=True).distinct()

    
    return render(request, 'account/user_home.html', {
        'jobs': jobs,
        'categories': categories,
        'locations': locations,
        'session_token': request.session.get('session_token'),
        'fullname': request.session.get('fullname'),
        'email': request.session.get('email'),
        'user_type': request.session.get('user_type'),
    })