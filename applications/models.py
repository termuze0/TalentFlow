from django.db import models
from account.models import CustomUser  
from jobs.models import Job

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True) 

    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"
class ApplicationStatus(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('REVIEWING', 'Reviewing'),
        ('INTERVIEW', 'Interview'),
        ('OFFERED', 'Offered'),
        ('REJECTED', 'Rejected'),
    ]

    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application.full_name} - {self.status}"