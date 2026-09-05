from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def public_home(request):
    """Public homepage view"""
    return render(request, 'index.html')

def public_profile(request):
    """Public village profile view"""
    return render(request, 'profile.html')

def public_population(request):
    """Public population data view"""
    return render(request, 'population.html')

def public_events(request):
    """Public events view"""
    return render(request, 'events.html')

def public_news(request):
    """Public news view"""
    return render(request, 'news.html')

def public_tourism(request):
    """Public tourism view"""
    return render(request, 'tourism.html')

def public_umkm(request):
    """Public UMKM/business view"""
    return render(request, 'umkm.html')

def public_organization(request):
    """Public organization structure view"""
    return render(request, 'organization.html')

def public_correspondence(request):
    """Public correspondence services view"""
    return render(request, 'correspondence.html')

def public_contact(request):
    """Public contact view"""
    return render(request, 'contact.html')
