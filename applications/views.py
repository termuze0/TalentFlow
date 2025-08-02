from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import JobApplication, ApplicationStatus
from jobs.models import Job
from account.models import UserSession
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')  
class ApplyJobView(View):
    def post(self, request, job_id):
       
        session_token = request.headers.get('X-Session-Token')
        user = None

        if session_token:
            try:
                session = UserSession.objects.get(session_token=session_token, is_active=True)
                if session.expires_at < timezone.now():
                    return JsonResponse({'error': 'Session expired'}, status=401)
                user = session.user
            except UserSession.DoesNotExist:
                return JsonResponse({'error': 'Invalid session token'}, status=401)

        job = get_object_or_404(Job, id=job_id)
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter')

        if not all([full_name, email, resume]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        application = JobApplication.objects.create(
            job=job,
            full_name=full_name,
            email=email,
            resume=resume,
            cover_letter=cover_letter,
            user=user
        )

        ApplicationStatus.objects.create(application=application, status='APPLIED')

        return JsonResponse({'message': 'Application submitted successfully'}, status=201)
@method_decorator(csrf_exempt, name='dispatch')
class MyApplicationsView(View):
    def get(self, request):
        return render(request, 'my_applications.html')

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

        applications = JobApplication.objects.filter(user=user).select_related('job', 'status').order_by('-submitted_at')

        data = [{
            'job_title': app.job.title,
            'submitted_at': app.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'status': app.status.status if hasattr(app, 'status') else 'UNKNOWN'
        } for app in applications]

        return JsonResponse({'applications': data}, status=200)
