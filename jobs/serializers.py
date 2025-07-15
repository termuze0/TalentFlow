from rest_framework import serializers
from .models import Job, Category, JobType, Tag
from account.models import CustomUser

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = ['id', 'type_name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'fullname', 'email', 'phone']

class JobSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    job_type = JobTypeSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    job_type_id = serializers.PrimaryKeyRelatedField(
        queryset=JobType.objects.all(), source='job_type', write_only=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, source='tags', write_only=True
    )

    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'description',
            'requirements',
            'location',
            'salary',
            'deadline',
            'posted_at',
            'is_active',
            'employer',
            'category',
            'job_type',
            'tags',
            'category_id',
            'job_type_id',
            'tag_ids',
        ]
