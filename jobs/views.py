from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Job,Category
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect


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