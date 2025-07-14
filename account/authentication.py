from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import UserSession, CustomUser
from django.utils import timezone

class CustomSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')

        if not token:
            raise AuthenticationFailed('No session token provided.')

        # Optional: Support "Token <token>" format
        if token.startswith("Token "):
            token = token.split(" ")[1]

        try:
            session = UserSession.objects.get(session_token=token, is_active=True)
        except UserSession.DoesNotExist:
            raise AuthenticationFailed('Invalid session token.')

        if session.expires_at < timezone.now():
            session.is_active = False
            session.save()
            raise AuthenticationFailed('Session expired.')

        return (session.user, None)
