from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Job,Category
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from account.models import UserSession
from django.http import JsonResponse
from jobs.models import SavedJob
from django.utils import timezone
def job_list_view(request):
    jobs = Job.objects.filter(is_active=True)
    categories = Category.objects.all()
    locations = Job.objects.values_list('location', flat=True).distinct()

    title = request.GET.get("title")
    location = request.GET.get("location")
    category = request.GET.get("category")

    if title:
        jobs = jobs.filter(title__icontains=title )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if category:
        jobs = jobs.filter(category__name__iexact=category)

    # Order by latest
    jobs = jobs.order_by("-posted_at")

    

    context = {
        "jobs": jobs,
        "categories": categories,
        "locations": locations,
    }

    return render(request, "account/user_home.html", context)

def job_detail_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, "jobs/job_detail.html", {"job": job})

class SavedJobView(APIView):
    def get(self, request):
        return render(request, 'jobs/job_saved.html')  # render HTML

    def post(self, request):
        session_token = request.headers.get('Session-Token')
        if not session_token:
            return JsonResponse({'error': 'Missing session token'}, status=401)

        try:
            session = UserSession.objects.get(session_token=session_token, is_active=True)
            if session.expires_at < timezone.now():
                return JsonResponse({'error': 'Session expired'}, status=401)
            user = session.user
        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session token'}, status=401)

        saved_jobs = SavedJob.objects.filter(user=user).select_related('job')
        jobs_data = [
            {
                'id': sj.job.id,
                'title': sj.job.title,
                'location': sj.job.location,
                'deadline': sj.job.deadline.strftime('%Y-%m-%d'),
                'category': sj.job.category.name if sj.job.category else '',
            }
            for sj in saved_jobs
        ]
        return JsonResponse({'saved_jobs': jobs_data})
class SaveJobView(APIView):
    def post(self, request, job_id):
        session_token = request.headers.get('Session-Token')
        if not session_token:
            return JsonResponse({'error': 'Missing session token'}, status=401)

        try:
            session = UserSession.objects.get(session_token=session_token, is_active=True)
            if session.expires_at < timezone.now():
                return JsonResponse({'error': 'Session expired'}, status=401)
            user = session.user
        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session token'}, status=401)

        job = get_object_or_404(Job, id=job_id)

        saved_job, created = SavedJob.objects.get_or_create(user=user, job=job)
        if created:
            return JsonResponse({'message': 'Job saved successfully'})
        else:
            saved_job.delete()
            return JsonResponse({'message': 'Job unsaved successfully'})
class CheckSavedStatusView(APIView):
    def get(self, request, job_id):
        session_token = request.headers.get('Session-Token')
        if not session_token:
            return JsonResponse({'error': 'Missing session token'}, status=401)

        try:
            session = UserSession.objects.get(session_token=session_token, is_active=True)
            if session.expires_at < timezone.now():
                return JsonResponse({'error': 'Session expired'}, status=401)
            user = session.user
        except UserSession.DoesNotExist:
            return JsonResponse({'error': 'Invalid session token'}, status=401)

        is_saved = SavedJob.objects.filter(user=user, job_id=job_id).exists()
        return JsonResponse({'saved': is_saved})