from django.db import models
from django.utils import timezone
from django.db.models import JSONField
from django.contrib.auth.hashers import make_password, check_password
import uuid

class CustomUser(models.Model):
    USER_TYPE = (
        ('JOB_SEEKER', 'Job Seeker'),
        ('EMPLOYER', 'Employer'),
    )
    email = models.EmailField(max_length=254, unique=True)
    fullname = models.CharField(max_length=50)
    user_type = models.CharField(max_length=50, choices=USER_TYPE)
    phone = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    joined = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.fullname} ({self.email})"

    def get_full_name(self):
        return self.fullname

    def is_employer(self):
        return self.user_type == 'EMPLOYER'

    def is_job_seeker(self):
        return self.user_type == 'JOB_SEEKER'
    @property
    def is_authenticated(self):
        return True

class EmployerProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='employer_profile')
    company_website = models.URLField(blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    social_media = JSONField(blank=True, null=True)

    def __str__(self):
        return f"Employer Profile for {self.user.fullname}"

    def get_social_link(self, provider):
        return self.social_media.get(provider) if self.social_media else None


class JobSeekerProfile(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='jobseeker_profile')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Job Seeker Profile for {self.user.fullname}"

    def has_resume(self):
        return bool(self.resume)


class UserCredential(models.Model):
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='credential')
    password_hash = models.CharField(max_length=255)
    otp_code = models.CharField(max_length=10, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    last_password_change = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Credentials for {self.user.fullname}"

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)


class SocialAccount(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='social_accounts')
    provider = models.CharField(max_length=50)
    provider_user_id = models.CharField(max_length=255)
    access_token = models.CharField(max_length=500, blank=True, null=True)
    refresh_token = models.CharField(max_length=500, blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('provider', 'provider_user_id')

    def __str__(self):
        return f"{self.provider} account for {self.user.fullname}"

    def is_token_expired(self):
        return self.token_expiry and self.token_expiry < timezone.now()


class UserSession(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='sessions')
    session_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Session {self.session_token} for {self.user.fullname}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def invalidate(self):
        self.is_active = False
        self.save()
