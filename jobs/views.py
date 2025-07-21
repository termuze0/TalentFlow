from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Job


# class JobListView(ListView):
#     model = Job
#     template_name = 'jobs/job_list.html'
#     context_object_name = 'jobs'
#     queryset = Job.objects.filter(is_active=True).order_by('-posted_at')


# class JobDetailView(DetailView):
#     model = Job
#     template_name = 'jobs/job_detail.html'
#     context_object_name = 'job'


# class JobCreateView(LoginReuqiredMixin, UserPassesTestMixin, CreateView):
#     model = Job
#     form_class = JobForm
#     template_name = 'jobs/job_form.html'
#     success_url = reverse_lazy('job_list')

#     def form_valid(self, form):
#         form.instance.employer = self.request.user
#         return super().form_valid(form)

#     def test_func(self):
#         return self.request.user.user_type == 'EMPLOYER'


# class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Job
#     form_class = JobForm
#     template_name = 'jobs/job_form.html'
#     success_url = reverse_lazy('job_list')

#     def test_func(self):
#         return self.get_object().employer == self.request.user


# class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
#     model = Job
#     template_name = 'jobs/job_confirm_delete.html'
#     success_url = reverse_lazy('job_list')

#     def test_func(self):
#         return self.get_object().employer == self.request.user

def job_list_view(request):
    jobs = Job.objects.filter(is_active=True)

    query = request.GET.get("q")
    location = request.GET.get("location")
    category = request.GET.get("category")
    job_type = request.GET.get("job_type")
    experience = request.GET.get("experience")
    salary = request.GET.get("salary")
    sort = request.GET.get("sort")

    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if location:
        jobs = jobs.filter(location__icontains=location)

    if category:
        jobs = jobs.filter(category__name__iexact=category)

    if job_type:
        jobs = jobs.filter(job_type__slug=job_type)

    if experience:
        jobs = jobs.filter(experience_level__iexact=experience)

    if salary:
        jobs = jobs.filter(salary__gte=int(salary))

    if sort == "salary":
        jobs = jobs.order_by("-salary")
    else:  # default: most recent
        jobs = jobs.order_by("-posted_at")

    paginator = Paginator(jobs, 10)
    page_number = request.GET.get("page")
    jobs_page = paginator.get_page(page_number)

    context = {
        "jobs": jobs_page,
        "it_jobs_count": Job.objects.filter(category__name__iexact="it").count(),
        "finance_jobs_count": Job.objects.filter(category__name__iexact="finance").count(),
        "healthcare_jobs_count": Job.objects.filter(category__name__iexact="healthcare").count(),
        "education_jobs_count": Job.objects.filter(category__name__iexact="education").count(),
    }

    return render(request, "account/user_home.html", context)


def job_detail_view(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, "account/job_detail.html", {"job": job})