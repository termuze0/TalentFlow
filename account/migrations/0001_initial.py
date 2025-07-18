# Generated by Django 5.2.1 on 2025-07-11 12:28

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('fullname', models.CharField(max_length=50)),
                ('user_type', models.CharField(choices=[('JOB_SEEKER', 'Job Seeker'), ('EMPLOYER', 'Employer')], max_length=50)),
                ('phone', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=False)),
                ('joined', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='EmployerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_website', models.URLField(blank=True, null=True)),
                ('company_description', models.TextField(blank=True, null=True)),
                ('company_logo', models.ImageField(blank=True, null=True, upload_to='company_logos/')),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('industry', models.CharField(blank=True, max_length=100, null=True)),
                ('founded_year', models.PositiveIntegerField(blank=True, null=True)),
                ('social_media', models.JSONField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employer_profile', to='account.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='JobSeekerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resume', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('bio', models.TextField(blank=True, null=True)),
                ('skills', models.TextField(blank=True, null=True)),
                ('education', models.TextField(blank=True, null=True)),
                ('experience', models.TextField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('portfolio_url', models.URLField(blank=True, null=True)),
                ('linkedin_url', models.URLField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='jobseeker_profile', to='account.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='UserCredential',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password_hash', models.CharField(max_length=255)),
                ('otp_code', models.CharField(blank=True, max_length=10, null=True)),
                ('otp_expiry', models.DateTimeField(blank=True, null=True)),
                ('last_password_change', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='credential', to='account.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='account.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='SocialAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(max_length=50)),
                ('provider_user_id', models.CharField(max_length=255)),
                ('access_token', models.CharField(blank=True, max_length=500, null=True)),
                ('refresh_token', models.CharField(blank=True, max_length=500, null=True)),
                ('token_expiry', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_accounts', to='account.customuser')),
            ],
            options={
                'unique_together': {('provider', 'provider_user_id')},
            },
        ),
    ]
