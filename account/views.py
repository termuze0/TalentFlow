from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render, redirect
from .serializers import RegistrationSerializer

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