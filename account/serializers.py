from rest_framework import serializers
from .models import CustomUser, EmployerProfile, JobSeekerProfile, UserCredential
class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    fullname = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=50)
    user_type = serializers.ChoiceField(choices=CustomUser.USER_TYPE)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user_type = validated_data.get('user_type')

        user = CustomUser.objects.create(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            phone=validated_data['phone'],
            user_type=user_type,
            is_active=True,
        )

        credential = UserCredential.objects.create(user=user)
        credential.set_password(password)

        if user_type == 'EMPLOYER':
            EmployerProfile.objects.create(user=user)
        else:  
            JobSeekerProfile.objects.create(user=user)

        return user
