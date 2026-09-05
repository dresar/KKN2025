from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.core.serializers import serialize
import json
from .models import VillageHistory, VillageHistoryPhoto
from .forms import VillageHistoryForm


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# Dashboard Views
def village_profile_dashboard(request):
    """Dashboard utama profil desa"""
    context = {
        'history_count': VillageHistory.objects.filter(is_active=True).count(),
        'featured_history': VillageHistory.objects.filter(is_featured=True, is_active=True)[:3],
        'recent_history': VillageHistory.objects.filter(is_active=True).order_by('-created_at')[:5]
    }
    return render(request, 'admin/modules/village_profile/dashboard.html', context)


def village_profile_overview(request):
    """Halaman overview profil desa untuk publik"""
    context = {
        'featured_histories': VillageHistory.objects.filter(is_featured=True, is_active=True)[:3],
        'recent_histories': VillageHistory.objects.filter(is_active=True).order_by('-created_at')[:6]
    }
    return render(request, 'admin/modules/village_profile/overview.html', context)


@login_required
@user_passes_test(is_admin)
def visi_misi_page(request):
    """Halaman visi misi desa"""
    return render(request, 'admin/modules/village_profile/visi_misi.html', {
        'title': 'Visi & Misi Desa'
    })


@login_required
@user_passes_test(is_admin)
def sejarah_page(request):
    """Halaman sejarah desa"""
    histories = VillageHistory.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'admin/modules/village_profile/sejarah.html', {
        'title': 'Sejarah Desa',
        'histories': histories
    })


@login_required
@user_passes_test(is_admin)
def geografis_page(request):
    """Halaman geografis desa"""
    return render(request, 'admin/modules/village_profile/geografis.html', {
        'title': 'Geografis Desa'
    })


@login_required
@user_passes_test(is_admin)
def peta_desa_page(request):
    """Halaman peta desa"""
    return render(request, 'admin/modules/village_profile/peta_desa.html', {
        'title': 'Peta Desa'
    })


# History Views
class VillageHistoryListView(ListView):
    """List view untuk sejarah desa"""
    model = VillageHistory
    template_name = 'admin/modules/village_profile/history/list.html'
    context_object_name = 'histories'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = VillageHistory.objects.all().order_by('-created_at')
        
        # Filter berdasarkan pencarian
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(summary__icontains=search)
            )
        
        # Filter berdasarkan tipe sejarah
        history_type = self.request.GET.get('history_type')
        if history_type:
            queryset = queryset.filter(history_type=history_type)
        
        # Filter berdasarkan status aktif
        is_active = self.request.GET.get('is_active')
        if is_active:
            queryset = queryset.filter(is_active=is_active == 'true')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['history_types'] = VillageHistory.HISTORY_TYPE_CHOICES
        return context


class VillageHistoryDetailView(DetailView):
    """Detail view untuk sejarah desa"""
    model = VillageHistory
    template_name = 'admin/modules/village_profile/history/detail.html'
    context_object_name = 'history'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.filter(is_active=True).order_by('display_order')
        return context


class VillageHistoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create view untuk sejarah desa"""
    model = VillageHistory
    form_class = VillageHistoryForm
    template_name = 'admin/modules/village_profile/history/form.html'
    success_url = reverse_lazy('village_profile:history_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Sejarah desa berhasil ditambahkan!')
        return super().form_valid(form)


class VillageHistoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update view untuk sejarah desa"""
    model = VillageHistory
    form_class = VillageHistoryForm
    template_name = 'admin/modules/village_profile/history/form.html'
    success_url = reverse_lazy('village_profile:history_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        messages.success(self.request, 'Sejarah desa berhasil diperbarui!')
        return super().form_valid(form)


class VillageHistoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete view untuk sejarah desa"""
    model = VillageHistory
    template_name = 'admin/modules/village_profile/history/confirm_delete.html'
    success_url = reverse_lazy('village_profile:history_list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Sejarah desa berhasil dihapus!')
        return super().delete(request, *args, **kwargs)


# Utility Views
def village_profile_stats(request):
    """API endpoint untuk statistik profil desa"""
    stats = {
        'history_count': VillageHistory.objects.filter(is_active=True).count(),
        'featured_history_count': VillageHistory.objects.filter(is_featured=True, is_active=True).count(),
        'total_photos': VillageHistoryPhoto.objects.filter(is_active=True).count()
    }
    return JsonResponse(stats)


def village_history_search(request):
    """Search endpoint untuk sejarah desa"""
    query = request.GET.get('q', '')
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    histories = VillageHistory.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(summary__icontains=query),
        is_active=True
    )[:10]
    
    results = []
    for history in histories:
        results.append({
            'id': history.id,
            'title': history.title,
            'summary': history.summary[:100] + '...' if len(history.summary) > 100 else history.summary,
            'url': reverse('village_profile:history_detail', kwargs={'pk': history.pk})
        })
    
    return JsonResponse({'results': results})


def village_history_export(request):
    """Export sejarah desa ke JSON"""
    histories = VillageHistory.objects.filter(is_active=True)
    data = serialize('json', histories)
    
    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="village_history.json"'
    return response