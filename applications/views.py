from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
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