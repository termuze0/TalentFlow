from django.db import models
from django.utils import timezone
from account.models import CustomUser  
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class JobType(models.Model):
    type_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.type_name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    employer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'EMPLOYER'})
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deadline = models.DateField()
    job_type = models.ForeignKey(JobType, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
