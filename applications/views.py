from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import JobApplication, ApplicationStatus
from jobs.models import Job
from account.models import UserSession
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import requests,json
import fitz
@method_decorator(csrf_exempt, name='dispatch')  
class ApplyJobView(View):
    def post(self, request, job_id):
       
        session_token = request.headers.get('Session-Token')
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
@method_decorator(csrf_exempt, name='dispatch')
class ResumeUploadView(View):
    def get(self, request):
        return render(request, 'resume_upload.html')

    def post(self, request):
        resume_file = request.FILES.get('resume_file')
        if not resume_file:
            return JsonResponse({'error': 'Please upload a resume file.'}, status=400)

        if not resume_file.name.endswith('.pdf'):
            return JsonResponse({'error': 'Only PDF files are supported currently.'}, status=400)

        try:
            text = self.extract_text_from_pdf(resume_file)
            ai_response = self.call_gemini_api(text)

            return JsonResponse({
                'ai_response': ai_response,
                'resume_text': text[:1000]
            })
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

    def extract_text_from_pdf(self, file):
        """Extracts text from a PDF file."""
        doc = fitz.open(stream=file.read(), filetype='pdf')
        text = ''.join(page.get_text() for page in doc)
        return text

    def call_gemini_api(self, resume_text: str) -> dict:
        """
        Analyzes a resume using the Gemini 1.5 Flash API and returns a structured JSON response.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={settings.GEMINI_API_KEY}"

        prompt_template = """
        You are an AI resume analyzer.

        Analyze the following text as a resume. If the text is a valid resume,
        return a JSON object with the following keys:
        - summary: a brief overall summary
        - strengths: a list of key strengths
        - improvements: a list of areas for improvement
        - skills: a list of key skills mentioned
        - experience_level: the estimated experience level (e.g., Junior, Mid-level, Senior)
        - recommendations: advice for the candidate

        If the text is NOT a valid resume, return the following JSON object:
        {{"summary": "Text is not a resume", "strengths": [], "improvements": [], "skills": [], "experience_level": "N/A", "recommendations": "Please provide a valid resume."}}

        Respond ONLY with the JSON object. Do not include any other text or formatting outside of the JSON.

        Resume text to analyze:
        \"\"\"
        {resume_text}
        \"\"\"
        """
        
        # The prompt template is formatted here.
        formatted_prompt = prompt_template.format(resume_text=resume_text)

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": formatted_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 500,
                "responseMimeType": "application/json",
            },
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            
            content_part = data.get("candidates", [])[0].get("content", {}).get("parts", [{}])[0]
            if content_part and "text" in content_part:
                # The API is configured to return JSON, but it's good practice to parse it.
                return json.loads(content_part["text"])

            return {"error": "Failed to extract content from Gemini API response"}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error calling Gemini API: {str(e)}"}
        except (json.JSONDecodeError, IndexError) as e:
            return {"error": f"Failed to parse AI response: {e}"}