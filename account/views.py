from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect
from .models import CustomUser, UserCredential,UserSession
from .serializers import RegistrationSerializer,LoginSerializer
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