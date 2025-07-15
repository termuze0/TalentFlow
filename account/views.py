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

@api_view(['POST'])
def social_login(request):
    serializer = SocialLoginSerializer(data=request.data)
    if serializer.is_valid():
        provider = serializer.validated_data['provider']
        token = serializer.validated_data['access_token']

        if provider == 'google':
            google_url = f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}'
            resp = requests.get(google_url)
            if resp.status_code != 200:
                return Response({'error': 'Invalid Google token'}, status=400)
            data = resp.json()
            email = data.get('email')
            fullname = data.get('name')
            provider_user_id = data.get('sub')

            if not email or not provider_user_id:
                return Response({'error': 'Missing fields from Google'}, status=400)

            user, _ = CustomUser.objects.get_or_create(email=email, defaults={
                'fullname': fullname,
                'user_type': 'JOB_SEEKER',  # or 'EMPLOYER' depending on context
                'is_active': True,
                'joined': timezone.now()
            })

            # Create or update SocialAccount
            SocialAccount.objects.update_or_create(
                user=user,
                provider='google',
                provider_user_id=provider_user_id,
                defaults={
                    'access_token': token,
                    'token_expiry': timezone.now()  # Or extract expiry from Google
                }
            )

            # Create custom session
            session = UserSession.objects.create(user=user, expires_at=timezone.now() + timezone.timedelta(days=7))
            return Response({
                'message': 'Login via Google successful',
                'session_token': str(session.session_token),
                'user': {
                    'email': user.email,
                    'fullname': user.fullname,
                    'user_type': user.user_type
                }
            })

        return Response({'error': 'Unsupported provider'}, status=400)

    return Response(serializer.errors, status=400)
def UserhomePage(request):
    return render(request, 'user_home.html')