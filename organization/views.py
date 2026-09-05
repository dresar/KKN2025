from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Case, When, IntegerField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.db import transaction
import json
import logging
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from .models import PerangkatDesa, LembagaAdat, PenggerakPKK, Kepemudaan, KarangTaruna
from .forms import PerangkatDesaForm, LembagaAdatForm, PenggerakPKKForm, KepemudaanForm, KarangTarunaForm
from references.models import Penduduk

logger = logging.getLogger(__name__)

# Error handling utilities
def handle_api_error(e, operation="operation", logger=None):
    """Handle API errors with specific error types and logging"""
    if logger:
        logger.error(f"Error during {operation}: {str(e)}", exc_info=True)
    
    if isinstance(e, ValidationError):
        return JsonResponse({
            'success': False,
            'error': 'Validation error',
            'details': e.message_dict if hasattr(e, 'message_dict') else str(e)
        }, status=400)
    elif isinstance(e, ObjectDoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Data tidak ditemukan',
            'details': str(e)
        }, status=404)
    elif isinstance(e, IntegrityError):
        return JsonResponse({
            'success': False,
            'error': 'Data integrity error - mungkin ada duplikasi data',
            'details': 'Periksa kembali data yang diinput'
        }, status=400)
    elif isinstance(e, json.JSONDecodeError):
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format',
            'details': 'Format data tidak valid'
        }, status=400)
    else:
        return JsonResponse({
            'success': False,
            'error': 'Internal server error',
            'details': str(e) if logger else 'Terjadi kesalahan sistem'
        }, status=500)

# Pagination configuration
PAGE_SIZE_OPTIONS = [10, 25, 50, 100]
DEFAULT_PAGE_SIZE = 10

# ===== HELPER FUNCTIONS =====
def get_paginated_data(request, queryset, page_size=DEFAULT_PAGE_SIZE):
    """Helper function for consistent pagination across all views"""
    try:
        page_size = int(request.GET.get('page_size', page_size))
        if page_size not in PAGE_SIZE_OPTIONS:
            page_size = DEFAULT_PAGE_SIZE
    except (ValueError, TypeError):
        page_size = DEFAULT_PAGE_SIZE
    
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'page_size': page_size,
        'page_size_options': PAGE_SIZE_OPTIONS,
        'total_count': paginator.count,
        'page_range': paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
    }

def handle_search_and_filter(queryset, request, search_fields, filter_fields=None):
    """Helper function for consistent search and filtering"""
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        search_q = Q()
        for field in search_fields:
            search_q |= Q(**{f"{field}__icontains": search_query})
        queryset = queryset.filter(search_q)
    
    if filter_fields:
        for field_name, choices in filter_fields.items():
            filter_value = request.GET.get(field_name, '')
            if filter_value:
                queryset = queryset.filter(**{field_name: filter_value})
    
    return queryset, search_query

# ===== ADMIN DASHBOARD =====
@login_required
def organization_admin(request):
    """Dashboard admin untuk modul organisasi"""
    context = {
        'perangkat_count': PerangkatDesa.objects.count(),
        'lembaga_adat_count': LembagaAdat.objects.count(),
        'penggerak_pkk_count': PenggerakPKK.objects.count(),
        'kepemudaan_count': Kepemudaan.objects.count(),
        'karang_taruna_count': KarangTaruna.objects.count(),
        'active_perangkat': PerangkatDesa.objects.filter(status='aktif').count(),
        'active_lembaga': LembagaAdat.objects.filter(status='aktif').count(),
        'active_pkk': PenggerakPKK.objects.filter(status='aktif').count(),
        'active_kepemudaan': Kepemudaan.objects.filter(status='aktif').count(),
        'active_karang_taruna': KarangTaruna.objects.filter(status='aktif').count(),
    }
    return render(request, 'admin/modules/organization/dashboard.html', context)


# ===== PERANGKAT DESA VIEWS =====
@login_required
def perangkat_list(request):
    """List view untuk perangkat desa dengan pagination dan filtering optimal"""
    try:
        # Base queryset with optimized joins
        perangkat_queryset = PerangkatDesa.objects.select_related('penduduk').annotate(
            jabatan_order=Case(
                When(jabatan='kepala_desa', then=1),
                When(jabatan='sekretaris_desa', then=2),
                When(jabatan='kaur_pemerintahan', then=3),
                When(jabatan='kaur_pembangunan', then=4),
                When(jabatan='kaur_kesra', then=5),
                When(jabatan='kaur_keuangan', then=6),
                When(jabatan='kaur_umum', then=7),
                When(jabatan='kasi_pemerintahan', then=8),
                When(jabatan='kasi_pembangunan', then=9),
                When(jabatan='kasi_kesra', then=10),
                When(jabatan='kepala_dusun', then=11),
                When(jabatan='staf', then=12),
                default=99,
                output_field=IntegerField()
            )
        ).order_by('jabatan_order', 'penduduk__name')
        
        # Handle search and filtering
        search_fields = ['penduduk__name', 'jabatan', 'nip', 'deskripsi_tugas']
        filter_fields = {
            'jabatan': dict(PerangkatDesa.JABATAN_CHOICES),
            'status': dict(PerangkatDesa.STATUS_CHOICES)
        }
        
        perangkat_queryset, search_query = handle_search_and_filter(
            perangkat_queryset, request, search_fields, filter_fields
        )
        
        # Calculate statistics before pagination
        stats = perangkat_queryset.aggregate(
            total_count=Count('id'),
            active_count=Count(Case(When(status='aktif', then=1))),
            inactive_count=Count(Case(When(status='non_aktif', then=1))),
            pensiun_count=Count(Case(When(status='pensiun', then=1)))
        )
        
        # Get paginated data
        pagination_data = get_paginated_data(request, perangkat_queryset)
        
        context = {
            **pagination_data,
            'search_query': search_query,
            'jabatan_filter': request.GET.get('jabatan', ''),
            'status_filter': request.GET.get('status', ''),
            'jabatan_choices': PerangkatDesa.JABATAN_CHOICES,
            'status_choices': PerangkatDesa.STATUS_CHOICES,
            **stats
        }
        
        return render(request, 'admin/modules/organization/perangkat_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in perangkat_list: {str(e)}")
        messages.error(request, 'Terjadi kesalahan saat memuat data perangkat desa.')
        return render(request, 'admin/modules/organization/perangkat_list.html', {
            'page_obj': None,
            'error': True
        })


@login_required
@csrf_protect
def perangkat_add(request):
    """Add view untuk perangkat desa dengan CSRF protection"""
    try:
        if request.method == 'POST':
            with transaction.atomic():
                form = PerangkatDesaForm(request.POST, request.FILES)
                if form.is_valid():
                    # Check for duplicate entries
                    penduduk = form.cleaned_data['penduduk']
                    jabatan = form.cleaned_data['jabatan']
                    
                    existing = PerangkatDesa.objects.filter(
                        penduduk=penduduk, 
                        jabatan=jabatan,
                        status='aktif'
                    ).exists()
                    
                    if existing:
                        messages.error(request, f'{penduduk.name} sudah terdaftar sebagai {jabatan} dengan status aktif.')
                        return render(request, 'admin/modules/organization/perangkat_desa_form.html', {
                            'form': form,
                            'title': 'Tambah Perangkat Desa',
                            'submit_text': 'Simpan',
                            'csrf_token': get_token(request)
                        })
                    
                    perangkat = form.save()
                    messages.success(request, f'Data perangkat desa {perangkat.penduduk.name} berhasil ditambahkan.')
                    return redirect('organization:perangkat_list')
                else:
                    messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
        else:
            form = PerangkatDesaForm()
        
        context = {
            'form': form,
            'title': 'Tambah Perangkat Desa',
            'submit_text': 'Simpan',
            'csrf_token': get_token(request)
        }
        return render(request, 'admin/modules/organization/perangkat_desa_form.html', context)
        
    except Exception as e:
        logger.error(f"Error in perangkat_add: {str(e)}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('organization:perangkat_list')


@login_required
@csrf_protect
def perangkat_edit(request, pk):
    """Edit view untuk perangkat desa dengan CSRF protection"""
    try:
        perangkat = get_object_or_404(PerangkatDesa, pk=pk)
        
        if request.method == 'POST':
            with transaction.atomic():
                form = PerangkatDesaForm(request.POST, request.FILES, instance=perangkat)
                if form.is_valid():
                    # Check for duplicate entries (excluding current instance)
                    penduduk = form.cleaned_data['penduduk']
                    jabatan = form.cleaned_data['jabatan']
                    
                    existing = PerangkatDesa.objects.filter(
                        penduduk=penduduk, 
                        jabatan=jabatan,
                        status='aktif'
                    ).exclude(pk=perangkat.pk).exists()
                    
                    if existing:
                        messages.error(request, f'{penduduk.name} sudah terdaftar sebagai {jabatan} dengan status aktif.')
                        return render(request, 'admin/modules/organization/perangkat_desa_form.html', {
                            'form': form,
                            'title': f'Edit Perangkat Desa - {perangkat.penduduk.name}',
                            'object': perangkat,
                            'submit_text': 'Update',
                            'csrf_token': get_token(request)
                        })
                    
                    perangkat = form.save()
                    messages.success(request, f'Data perangkat desa {perangkat.penduduk.name} berhasil diperbarui.')
                    return redirect('organization:perangkat_list')
                else:
                    messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
        else:
            form = PerangkatDesaForm(instance=perangkat)
        
        context = {
            'form': form,
            'title': f'Edit Perangkat Desa - {perangkat.penduduk.name}',
            'object': perangkat,
            'submit_text': 'Update',
            'csrf_token': get_token(request)
        }
        return render(request, 'admin/modules/organization/perangkat_desa_form.html', context)
        
    except Exception as e:
        logger.error(f"Error in perangkat_edit: {str(e)}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('organization:perangkat_list')


@login_required
@csrf_protect
@require_POST
def perangkat_delete(request, pk):
    """Delete view untuk perangkat desa dengan CSRF protection"""
    try:
        perangkat = get_object_or_404(PerangkatDesa, pk=pk)
        
        with transaction.atomic():
            nama = perangkat.penduduk.name
            perangkat.delete()
            messages.success(request, f'Data perangkat desa {nama} berhasil dihapus.')
            
        return redirect('organization:perangkat_list')
        
    except Exception as e:
        logger.error(f"Error in perangkat_delete: {str(e)}")
        messages.error(request, 'Terjadi kesalahan saat menghapus data. Silakan coba lagi.')
        return redirect('organization:perangkat_list')


@login_required
def perangkat_detail(request, pk):
    """Detail view untuk perangkat desa"""
    perangkat = get_object_or_404(PerangkatDesa, pk=pk)
    context = {
        'object': perangkat,
        'title': f'Detail Perangkat Desa - {perangkat.penduduk.name}'
    }
    return render(request, 'admin/modules/organization/perangkat_desa_detail.html', context)


# ===== LEMBAGA ADAT VIEWS =====
@login_required
def lembaga_adat_list(request):
    """List view untuk lembaga adat dengan pagination optimal"""
    try:
        lembaga_queryset = LembagaAdat.objects.select_related('ketua', 'sekretaris', 'bendahara').all()
        
        # Define search and filter fields
        search_fields = ['nama_lembaga', 'jenis_lembaga', 'ketua__name', 'deskripsi']
        filter_fields = {
            'jenis': dict(LembagaAdat.JENIS_LEMBAGA_CHOICES),
            'status': dict(LembagaAdat.STATUS_CHOICES)
        }
        
        lembaga_queryset, search_query = handle_search_and_filter(
            lembaga_queryset, request, search_fields, filter_fields
        )
        
        # Order by nama_lembaga
        lembaga_queryset = lembaga_queryset.order_by('nama_lembaga')
        
        # Calculate statistics before pagination
        stats = lembaga_queryset.aggregate(
            total_count=Count('id'),
            active_count=Count(Case(When(status='aktif', then=1))),
            inactive_count=Count(Case(When(status='non_aktif', then=1)))
        )
        
        # Get paginated data
        pagination_data = get_paginated_data(request, lembaga_queryset)
        
        context = {
            **pagination_data,
            'search_query': search_query,
            'jenis_filter': request.GET.get('jenis', ''),
            'status_filter': request.GET.get('status', ''),
            'jenis_choices': LembagaAdat.JENIS_LEMBAGA_CHOICES,
            'status_choices': LembagaAdat.STATUS_CHOICES,
            **stats
        }
        
        return render(request, 'admin/modules/organization/lembaga_adat_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in lembaga_adat_list: {str(e)}")
        messages.error(request, 'Terjadi kesalahan saat memuat data lembaga adat.')
        return render(request, 'admin/modules/organization/lembaga_adat_list.html', {
             'page_obj': None,
             'error': True
         })


@login_required
@csrf_protect
def lembaga_adat_add(request):
    """Add view untuk lembaga adat dengan CSRF protection"""
    try:
        if request.method == 'POST':
            with transaction.atomic():
                form = LembagaAdatForm(request.POST, request.FILES)
                if form.is_valid():
                    # Check for duplicate entries
                    nama_lembaga = form.cleaned_data['nama_lembaga']
                    
                    existing = LembagaAdat.objects.filter(
                        nama_lembaga__iexact=nama_lembaga,
                        status='aktif'
                    ).exists()
                    
                    if existing:
                        messages.error(request, f'Lembaga adat dengan nama "{nama_lembaga}" sudah terdaftar dengan status aktif.')
                        return render(request, 'admin/modules/organization/lembaga_adat_form.html', {
                            'form': form,
                            'title': 'Tambah Lembaga Adat',
                            'submit_text': 'Simpan',
                            'csrf_token': get_token(request)
                        })
                    
                    lembaga = form.save()
                    messages.success(request, f'Data lembaga adat {lembaga.nama_lembaga} berhasil ditambahkan.')
                    return redirect('organization:lembaga_adat_list')
                else:
                    messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
        else:
            form = LembagaAdatForm()
        
        context = {
            'form': form,
            'title': 'Tambah Lembaga Adat',
            'submit_text': 'Simpan',
            'csrf_token': get_token(request)
        }
        return render(request, 'admin/modules/organization/lembaga_adat_form.html', context)
        
    except Exception as e:
        logger.error(f"Error in lembaga_adat_add: {str(e)}")
        messages.error(request, 'Terjadi kesalahan sistem. Silakan coba lagi.')
        return redirect('organization:lembaga_adat_list')


@login_required
def lembaga_adat_edit(request, pk):
    """Edit view untuk lembaga adat"""
    lembaga = get_object_or_404(LembagaAdat, pk=pk)
    
    if request.method == 'POST':
        form = LembagaAdatForm(request.POST, request.FILES, instance=lembaga)
        if form.is_valid():
            lembaga = form.save()
            messages.success(request, f'Data lembaga adat {lembaga.nama_lembaga} berhasil diperbarui.')
            return redirect('organization:lembaga_adat_list')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
    else:
        form = LembagaAdatForm(instance=lembaga)
    
    context = {
        'form': form,
        'title': f'Edit Lembaga Adat - {lembaga.nama_lembaga}',
        'object': lembaga,
        'submit_text': 'Update'
    }
    return render(request, 'admin/modules/organization/lembaga_adat_form.html', context)


@login_required
def lembaga_adat_delete(request, pk):
    """Delete view untuk lembaga adat"""
    lembaga = get_object_or_404(LembagaAdat, pk=pk)
    
    if request.method == 'POST':
        nama = lembaga.nama_lembaga
        lembaga.delete()
        messages.success(request, f'Data lembaga adat {nama} berhasil dihapus.')
        return redirect('organization:lembaga_adat_list')
    
    context = {
        'object': lembaga,
        'title': f'Hapus Lembaga Adat - {lembaga.nama_lembaga}'
    }
    return render(request, 'admin/modules/organization/lembaga_adat_confirm_delete.html', context)


@login_required
def lembaga_adat_detail(request, pk):
    """Detail view untuk lembaga adat"""
    lembaga = get_object_or_404(LembagaAdat, pk=pk)
    context = {
        'object': lembaga,
        'title': f'Detail Lembaga Adat - {lembaga.nama_lembaga}'
    }
    return render(request, 'admin/modules/organization/lembaga_adat_detail.html', context)


# ===== PENGGERAK PKK VIEWS =====
@login_required
def penggerak_pkk_list(request):
    """List view untuk penggerak PKK"""
    search_query = request.GET.get('search', '')
    jabatan_filter = request.GET.get('jabatan', '')
    status_filter = request.GET.get('status', '')
    
    pkk_queryset = PenggerakPKK.objects.select_related('penduduk').all()
    
    if search_query:
        pkk_queryset = pkk_queryset.filter(
            Q(penduduk__name__icontains=search_query) |
            Q(jabatan__icontains=search_query) |
            Q(nomor_anggota__icontains=search_query) |
            Q(keahlian__icontains=search_query)
        )
    
    if jabatan_filter:
        pkk_queryset = pkk_queryset.filter(jabatan=jabatan_filter)
    
    if status_filter:
        pkk_queryset = pkk_queryset.filter(status=status_filter)
    
    pkk_queryset = pkk_queryset.order_by('jabatan', 'penduduk__name')
    
    # Calculate statistics
    total_count = pkk_queryset.count()
    active_count = pkk_queryset.filter(status='aktif').count()
    inactive_count = pkk_queryset.filter(status='non_aktif').count()
    
    paginator = Paginator(pkk_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'jabatan_choices': PenggerakPKK.JABATAN_PKK_CHOICES,
        'status_choices': PenggerakPKK.STATUS_CHOICES,
    }
    return render(request, 'admin/modules/organization/penggerak_pkk_list.html', context)


@login_required
def penggerak_pkk_add(request):
    """Add view untuk penggerak PKK"""
    if request.method == 'POST':
        form = PenggerakPKKForm(request.POST, request.FILES)
        if form.is_valid():
            pkk = form.save()
            messages.success(request, f'Data penggerak PKK {pkk.penduduk.name} berhasil ditambahkan.')
            return redirect('organization:penggerak_pkk_list')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
    else:
        form = PenggerakPKKForm()
    
    context = {
        'form': form,
        'title': 'Tambah Penggerak PKK',
        'submit_text': 'Simpan'
    }
    return render(request, 'admin/modules/organization/penggerak_pkk_form.html', context)


@login_required
def penggerak_pkk_edit(request, pk):
    """Edit view untuk penggerak PKK"""
    pkk = get_object_or_404(PenggerakPKK, pk=pk)
    
    if request.method == 'POST':
        form = PenggerakPKKForm(request.POST, request.FILES, instance=pkk)
        if form.is_valid():
            pkk = form.save()
            messages.success(request, f'Data penggerak PKK {pkk.penduduk.name} berhasil diperbarui.')
            return redirect('organization:penggerak_pkk_list')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
    else:
        form = PenggerakPKKForm(instance=pkk)
    
    context = {
        'form': form,
        'title': f'Edit Penggerak PKK - {pkk.penduduk.name}',
        'object': pkk,
        'submit_text': 'Update'
    }
    return render(request, 'admin/modules/organization/penggerak_pkk_form.html', context)


@login_required
def penggerak_pkk_delete(request, pk):
    """Delete view untuk penggerak PKK"""
    pkk = get_object_or_404(PenggerakPKK, pk=pk)
    
    if request.method == 'POST':
        nama = pkk.penduduk.name
        pkk.delete()
        messages.success(request, f'Data penggerak PKK {nama} berhasil dihapus.')
        return redirect('organization:penggerak_pkk_list')
    
    context = {
        'object': pkk,
        'title': f'Hapus Penggerak PKK - {pkk.penduduk.name}'
    }
    return render(request, 'admin/modules/organization/penggerak_pkk_confirm_delete.html', context)


@login_required
def penggerak_pkk_detail(request, pk):
    """Detail view untuk penggerak PKK"""
    pkk = get_object_or_404(PenggerakPKK, pk=pk)
    context = {
        'object': pkk,
        'title': f'Detail Penggerak PKK - {pkk.penduduk.name}'
    }
    return render(request, 'admin/modules/organization/penggerak_pkk_detail.html', context)


# ===== KEPEMUDAAN VIEWS =====
@login_required
def kepemudaan_list(request):
    """List view untuk kepemudaan"""
    search_query = request.GET.get('search', '')
    jenis_filter = request.GET.get('jenis', '')
    status_filter = request.GET.get('status', '')
    
    kepemudaan_queryset = Kepemudaan.objects.select_related('ketua').all()
    
    if search_query:
        kepemudaan_queryset = kepemudaan_queryset.filter(
            Q(nama_organisasi__icontains=search_query) |
            Q(jenis_organisasi__icontains=search_query) |
            Q(ketua__name__icontains=search_query) |
            Q(deskripsi__icontains=search_query)
        )
    
    if jenis_filter:
        kepemudaan_queryset = kepemudaan_queryset.filter(jenis_organisasi=jenis_filter)
    
    if status_filter:
        kepemudaan_queryset = kepemudaan_queryset.filter(status=status_filter)
    
    kepemudaan_queryset = kepemudaan_queryset.order_by('nama_organisasi')
    
    # Calculate statistics
    total_count = kepemudaan_queryset.count()
    active_count = kepemudaan_queryset.filter(status='aktif').count()
    inactive_count = kepemudaan_queryset.filter(status='non_aktif').count()
    
    paginator = Paginator(kepemudaan_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'jenis_filter': jenis_filter,
        'status_filter': status_filter,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'jenis_choices': Kepemudaan.JENIS_ORGANISASI_CHOICES,
        'status_choices': Kepemudaan.STATUS_CHOICES,
    }
    return render(request, 'admin/modules/organization/kepemudaan_list.html', context)


@login_required
def kepemudaan_add(request):
    """Add view untuk kepemudaan"""
    if request.method == 'POST':
        form = KepemudaanForm(request.POST, request.FILES)
        if form.is_valid():
            kepemudaan = form.save()
            messages.success(request, f'Data kepemudaan {kepemudaan.nama_organisasi} berhasil ditambahkan.')
            return redirect('organization:kepemudaan_list')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
    else:
        form = KepemudaanForm()
    
    context = {
        'form': form,
        'title': 'Tambah Kepemudaan',
        'submit_text': 'Simpan'
    }
    return render(request, 'admin/modules/organization/kepemudaan_form.html', context)


@login_required
def kepemudaan_edit(request, pk):
    """Edit view untuk kepemudaan"""
    kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
    
    if request.method == 'POST':
        form = KepemudaanForm(request.POST, request.FILES, instance=kepemudaan)
        if form.is_valid():
            kepemudaan = form.save()
            messages.success(request, f'Data kepemudaan {kepemudaan.nama_organisasi} berhasil diperbarui.')
            return redirect('organization:kepemudaan_list')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
    else:
        form = KepemudaanForm(instance=kepemudaan)
    
    context = {
        'form': form,
        'title': f'Edit Kepemudaan - {kepemudaan.nama_organisasi}',
        'object': kepemudaan,
        'submit_text': 'Update'
    }
    return render(request, 'admin/modules/organization/kepemudaan_form.html', context)


@login_required
def kepemudaan_delete(request, pk):
    """Delete view untuk kepemudaan"""
    kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
    
    if request.method == 'POST':
        nama = kepemudaan.nama_organisasi
        kepemudaan.delete()
        messages.success(request, f'Data kepemudaan {nama} berhasil dihapus.')
        return redirect('organization:kepemudaan_list')
    
    context = {
        'object': kepemudaan,
        'title': f'Hapus Kepemudaan - {kepemudaan.nama_organisasi}'
    }
    return render(request, 'admin/modules/organization/kepemudaan_confirm_delete.html', context)


@login_required
def kepemudaan_detail(request, pk):
    """Detail view untuk kepemudaan"""
    kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
    context = {
        'object': kepemudaan,
        'title': f'Detail Kepemudaan - {kepemudaan.nama_organisasi}'
    }
    return render(request, 'admin/modules/organization/kepemudaan_detail.html', context)


# ===== KARANG TARUNA VIEWS =====
@login_required
def karang_taruna_list(request):
    """List view untuk karang taruna"""
    search_query = request.GET.get('search', '')
    jabatan_filter = request.GET.get('jabatan', '')
    status_filter = request.GET.get('status', '')
    pengurus_inti = request.GET.get('pengurus_inti', '')
    
    karang_queryset = KarangTaruna.objects.select_related('penduduk').all()
    
    if search_query:
        karang_queryset = karang_queryset.filter(
            Q(penduduk__name__icontains=search_query) |
            Q(jabatan__icontains=search_query) |
            Q(nomor_anggota__icontains=search_query) |
            Q(bidang_keahlian__icontains=search_query)
        )
    
    if jabatan_filter:
        karang_queryset = karang_queryset.filter(jabatan=jabatan_filter)
    
    if status_filter:
        karang_queryset = karang_queryset.filter(status=status_filter)
    
    if pengurus_inti:
        karang_queryset = karang_queryset.filter(is_pengurus_inti=pengurus_inti.lower() == 'true')
    
    karang_queryset = karang_queryset.order_by('jabatan', 'penduduk__name')
    
    # Calculate statistics
    total_count = karang_queryset.count()
    active_count = karang_queryset.filter(status='aktif').count()
    inactive_count = karang_queryset.filter(status='non_aktif').count()
    pengurus_inti_count = karang_queryset.filter(is_pengurus_inti=True).count()
    
    paginator = Paginator(karang_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'jabatan_filter': jabatan_filter,
        'status_filter': status_filter,
        'pengurus_inti': pengurus_inti,
        'total_count': total_count,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'pengurus_inti_count': pengurus_inti_count,
        'jabatan_choices': KarangTaruna.JABATAN_CHOICES,
        'status_choices': KarangTaruna.STATUS_CHOICES,
    }
    return render(request, 'admin/modules/organization/karang_taruna_list.html', context)


@login_required
def karang_taruna_add(request):
    """Add view untuk karang taruna"""
    if request.method == 'POST':
        form = KarangTarunaForm(request.POST, request.FILES)
        if form.is_valid():
            karang = form.save()
            messages.success(request, f'Data karang taruna {karang.penduduk.name} berhasil ditambahkan.')
            return redirect('organization:karang_taruna_list')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
    else:
        form = KarangTarunaForm()
    
    context = {
        'form': form,
        'title': 'Tambah Karang Taruna',
        'submit_text': 'Simpan'
    }
    return render(request, 'admin/modules/organization/karang_taruna_form.html', context)


@login_required
def karang_taruna_edit(request, pk):
    """Edit view untuk karang taruna"""
    karang = get_object_or_404(KarangTaruna, pk=pk)
    
    if request.method == 'POST':
        form = KarangTarunaForm(request.POST, request.FILES, instance=karang)
        if form.is_valid():
            karang = form.save()
            messages.success(request, f'Data karang taruna {karang.penduduk.name} berhasil diperbarui.')
            return redirect('organization:karang_taruna_list')
        else:
            messages.error(request, 'Terjadi kesalahan. Silakan periksa form kembali.')
    else:
        form = KarangTarunaForm(instance=karang)
    
    context = {
        'form': form,
        'title': f'Edit Karang Taruna - {karang.penduduk.name}',
        'object': karang,
        'submit_text': 'Update'
    }
    return render(request, 'admin/modules/organization/karang_taruna_form.html', context)


@login_required
def karang_taruna_delete(request, pk):
    """Delete view untuk karang taruna"""
    karang = get_object_or_404(KarangTaruna, pk=pk)
    
    if request.method == 'POST':
        nama = karang.penduduk.name
        karang.delete()
        messages.success(request, f'Data karang taruna {nama} berhasil dihapus.')
        return redirect('organization:karang_taruna_list')
    
    context = {
        'object': karang,
        'title': f'Hapus Karang Taruna - {karang.penduduk.name}'
    }
    return render(request, 'admin/modules/organization/karang_taruna_confirm_delete.html', context)


@login_required
def karang_taruna_detail(request, pk):
    """Detail view untuk karang taruna"""
    karang = get_object_or_404(KarangTaruna, pk=pk)
    context = {
        'object': karang,
        'title': f'Detail Karang Taruna - {karang.penduduk.name}'
    }
    return render(request, 'admin/modules/organization/karang_taruna_detail.html', context)


# ===== HELPER VIEWS =====
@require_http_methods(["GET"])
def api_penduduk_choices(request):
    """API untuk mendapatkan pilihan penduduk (untuk select2)"""
    search = request.GET.get('search', '')
    penduduk_list = Penduduk.objects.all()
    
    if search:
        penduduk_list = penduduk_list.filter(
            Q(name__icontains=search) |
            Q(nik__icontains=search)
        )
    
    results = []
    for penduduk in penduduk_list[:20]:  # Limit to 20 results
        results.append({
            'id': penduduk.id,
            'text': f"{penduduk.name} - {penduduk.nik}"
        })
    
    return JsonResponse({
        'results': results
    })


# ===== API VIEWS FOR CRUD OPERATIONS =====

# Perangkat Desa API Views
@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_perangkat_desa_list(request):
    """API untuk list perangkat desa"""
    try:
        perangkat_list = PerangkatDesa.objects.select_related('penduduk').all()
        
        # Search functionality
        search = request.GET.get('search', '').strip()
        if search:
            perangkat_list = perangkat_list.filter(
                Q(penduduk__name__icontains=search) |
                Q(jabatan__icontains=search) |
                Q(penduduk__nik__icontains=search)
            )
        
        # Filter by jabatan
        jabatan = request.GET.get('jabatan', '').strip()
        if jabatan:
            perangkat_list = perangkat_list.filter(jabatan=jabatan)
        
        # Filter by status
        status = request.GET.get('status', '').strip()
        if status:
            perangkat_list = perangkat_list.filter(status=status)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        paginator = Paginator(perangkat_list, 10)
        page_obj = paginator.get_page(page)
        
        results = []
        for perangkat in page_obj:
            # Handle foto profil URL
            foto_profil_url = None
            if perangkat.foto_profil:
                foto_profil_url = request.build_absolute_uri(perangkat.foto_profil.url)
            
            results.append({
                'id': perangkat.id,
                'penduduk_nama': perangkat.penduduk.name,
                'penduduk_nik': perangkat.penduduk.nik,
                'nama': perangkat.penduduk.name,
                'nik': perangkat.penduduk.nik,
                'jabatan': perangkat.get_jabatan_display(),
                'jabatan_code': perangkat.jabatan,
                'periode_mulai': perangkat.tanggal_mulai_tugas.strftime('%d/%m/%Y') if perangkat.tanggal_mulai_tugas else '',
                'periode_selesai': perangkat.tanggal_selesai_tugas.strftime('%d/%m/%Y') if perangkat.tanggal_selesai_tugas else None,
                'status': perangkat.get_status_display(),
                'status_code': perangkat.status,
                'status_display': perangkat.get_status_display(),
                'kontak_whatsapp': perangkat.kontak_whatsapp,
                'no_telepon': perangkat.kontak_whatsapp,
                'email_dinas': perangkat.email_dinas,
                'email': perangkat.email_dinas,
                'nip': perangkat.nip,
                'deskripsi_tugas': perangkat.deskripsi_tugas,
                'tanggal_mulai_tugas': perangkat.tanggal_mulai_tugas.strftime('%Y-%m-%d') if perangkat.tanggal_mulai_tugas else None,
                'tanggal_selesai_tugas': perangkat.tanggal_selesai_tugas.strftime('%Y-%m-%d') if perangkat.tanggal_selesai_tugas else None,
                'foto_profil': foto_profil_url,
            })
        
        # Calculate statistics from original queryset (before pagination)
        all_perangkat = PerangkatDesa.objects.all()
        statistics = {
            'total': all_perangkat.count(),
            'aktif': all_perangkat.filter(status='aktif').count(),
            'tidak_aktif': all_perangkat.filter(status='tidak_aktif').count(),
            'pensiun': all_perangkat.filter(status='pensiun').count(),
        }
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': paginator.count,
            'total_count': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'statistics': statistics,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving perangkat desa list", logger)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_perangkat_desa_detail(request, pk):
    """API untuk detail perangkat desa"""
    try:
        perangkat = get_object_or_404(PerangkatDesa, pk=pk)
        
        data = {
            'id': perangkat.id,
            'penduduk_id': perangkat.penduduk.id,
            'penduduk_nama': perangkat.penduduk.name,
            'penduduk_nik': perangkat.penduduk.nik,
            'nama': perangkat.penduduk.name,
            'nik': perangkat.penduduk.nik,
            'jabatan': perangkat.get_jabatan_display(),
            'jabatan_code': perangkat.jabatan,
            'jabatan_display': perangkat.get_jabatan_display(),
            'nip': perangkat.nip,
            'deskripsi_tugas': perangkat.deskripsi_tugas,
            'foto_profil': perangkat.foto_profil.url if perangkat.foto_profil else None,
            'kontak_whatsapp': perangkat.kontak_whatsapp,
            'no_telepon': perangkat.kontak_whatsapp,
            'email_dinas': perangkat.email_dinas,
            'email': perangkat.email_dinas,
            'status': perangkat.get_status_display(),
            'status_code': perangkat.status,
            'status_display': perangkat.get_status_display(),
            'tanggal_mulai_tugas': perangkat.tanggal_mulai_tugas.isoformat() if perangkat.tanggal_mulai_tugas else None,
            'tanggal_selesai_tugas': perangkat.tanggal_selesai_tugas.isoformat() if perangkat.tanggal_selesai_tugas else None,
            'periode_mulai': perangkat.tanggal_mulai_tugas.strftime('%d/%m/%Y') if perangkat.tanggal_mulai_tugas else None,
            'periode_selesai': perangkat.tanggal_selesai_tugas.strftime('%d/%m/%Y') if perangkat.tanggal_selesai_tugas else None,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return handle_api_error(e, "retrieving perangkat desa detail", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_perangkat_desa_create(request):
    """API untuk create perangkat desa"""
    try:
        data = json.loads(request.body)
        
        form = PerangkatDesaForm(data)
        if form.is_valid():
            with transaction.atomic():
                perangkat = form.save()
                logger.info(f"Perangkat desa created: {perangkat.id} - {perangkat.penduduk.name}")
                return JsonResponse({
                    'success': True,
                    'message': 'Data perangkat desa berhasil ditambahkan',
                    'data': {
                        'id': perangkat.id,
                        'penduduk_nama': perangkat.penduduk.name,
                        'penduduk_nik': perangkat.penduduk.nik,
                        'nama': perangkat.penduduk.name,
                        'nik': perangkat.penduduk.nik,
                        'jabatan': perangkat.get_jabatan_display(),
                        'jabatan_code': perangkat.jabatan,
                        'status': perangkat.get_status_display(),
                        'status_code': perangkat.status,
                        'periode_mulai': perangkat.tanggal_mulai_tugas.strftime('%d/%m/%Y') if perangkat.tanggal_mulai_tugas else None,
                        'no_telepon': perangkat.kontak_whatsapp,
                        'email': perangkat.email_dinas,
                    }
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError as e:
        return handle_api_error(e, "parsing JSON data", logger)
    except ValidationError as e:
        return handle_api_error(e, "validating perangkat desa data", logger)
    except IntegrityError as e:
        return handle_api_error(e, "creating perangkat desa", logger)
    except Exception as e:
        return handle_api_error(e, "creating perangkat desa", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_perangkat_desa_update(request, pk):
    """API untuk update perangkat desa"""
    try:
        perangkat = get_object_or_404(PerangkatDesa, pk=pk)
        
        form = PerangkatDesaForm(request.POST, request.FILES, instance=perangkat)
        if form.is_valid():
            with transaction.atomic():
                perangkat = form.save()
                logger.info(f"Perangkat desa updated: {perangkat.id} - {perangkat.penduduk.name}")
                return JsonResponse({
                    'success': True,
                    'message': 'Data perangkat desa berhasil diperbarui',
                    'data': {
                        'id': perangkat.id,
                        'penduduk_nama': perangkat.penduduk.name,
                        'penduduk_nik': perangkat.penduduk.nik,
                        'nama': perangkat.penduduk.name,
                        'nik': perangkat.penduduk.nik,
                        'jabatan': perangkat.get_jabatan_display(),
                        'jabatan_code': perangkat.jabatan,
                        'status': perangkat.get_status_display(),
                        'status_code': perangkat.status,
                        'periode_mulai': perangkat.tanggal_mulai_tugas.strftime('%d/%m/%Y') if perangkat.tanggal_mulai_tugas else None,
                        'no_telepon': perangkat.kontak_whatsapp,
                        'email': perangkat.email_dinas,
                    }
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'errors': form.errors
            }, status=400)
    except ObjectDoesNotExist as e:
        return handle_api_error(e, "finding perangkat desa", logger)
    except ValidationError as e:
        return handle_api_error(e, "validating perangkat desa data", logger)
    except IntegrityError as e:
        return handle_api_error(e, "updating perangkat desa", logger)
    except Exception as e:
        return handle_api_error(e, "updating perangkat desa", logger)


@csrf_protect
@require_http_methods(["DELETE"])
def api_perangkat_desa_delete(request, pk):
    """API untuk delete perangkat desa"""
    try:
        perangkat = get_object_or_404(PerangkatDesa, pk=pk)
        nama = perangkat.penduduk.name
        
        with transaction.atomic():
            perangkat.delete()
            logger.info(f"Perangkat desa deleted: {pk} - {nama}")
            
        return JsonResponse({
            'success': True,
            'message': f'Data perangkat desa {nama} berhasil dihapus'
        })
    except ObjectDoesNotExist as e:
        return handle_api_error(e, "finding perangkat desa to delete", logger)
    except IntegrityError as e:
        return handle_api_error(e, "deleting perangkat desa", logger)
    except Exception as e:
        return handle_api_error(e, "deleting perangkat desa", logger)


# Lembaga Adat API Views
@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_lembaga_adat_list(request):
    """API untuk list lembaga adat"""
    try:
        lembaga_list = LembagaAdat.objects.select_related('ketua').all()
        
        # Search functionality
        search = request.GET.get('search', '')
        if search:
            lembaga_list = lembaga_list.filter(
                Q(nama_lembaga__icontains=search) |
                Q(ketua__name__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        paginator = Paginator(lembaga_list, 10)
        page_obj = paginator.get_page(page)
        
        results = []
        for lembaga in page_obj:
            results.append({
                'id': lembaga.id,
                'nama_lembaga': lembaga.nama_lembaga,
                'jenis_lembaga': lembaga.get_jenis_lembaga_display(),
                'jenis_code': lembaga.jenis_lembaga,
                'ketua_nama': lembaga.ketua.name if lembaga.ketua else None,
                'sekretaris_nama': lembaga.sekretaris.name if lembaga.sekretaris else None,
                'bendahara_nama': lembaga.bendahara.name if lembaga.bendahara else None,
                'deskripsi': lembaga.deskripsi,
                'kegiatan_rutin': lembaga.kegiatan_rutin,
                'jumlah_anggota': lembaga.jumlah_anggota,
                'tanggal_terbentuk': lembaga.tanggal_terbentuk.isoformat() if lembaga.tanggal_terbentuk else None,
                'alamat_sekretariat': lembaga.alamat_sekretariat,
                'kontak_phone': lembaga.kontak_phone,
                'foto_kegiatan': lembaga.foto_kegiatan.url if lembaga.foto_kegiatan else None,
                'status': lembaga.get_status_display(),
                'status_code': lembaga.status,
            })
        
        # Calculate statistics
        statistics = {
            'total': paginator.count,
            'aktif': lembaga_list.filter(status='aktif').count(),
            'tidak_aktif': lembaga_list.filter(status='tidak_aktif').count(),
            'nonaktif': lembaga_list.filter(status='nonaktif').count(),
        }
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': paginator.count,
            'total_count': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'statistics': statistics,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except ObjectDoesNotExist as e:
        return handle_api_error(e, "finding lembaga adat detail", logger)
    except Exception as e:
        return handle_api_error(e, "retrieving lembaga adat detail", logger)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_lembaga_adat_detail(request, pk):
    """API untuk detail lembaga adat"""
    try:
        lembaga = get_object_or_404(LembagaAdat, pk=pk)
        
        data = {
            'id': lembaga.id,
            'nama_lembaga': lembaga.nama_lembaga,
            'jenis_lembaga': lembaga.get_jenis_lembaga_display(),
            'ketua_id': lembaga.ketua.id if lembaga.ketua else None,
            'ketua_nama': lembaga.ketua.name if lembaga.ketua else None,
            'status': lembaga.get_status_display(),
            'tanggal_terbentuk': lembaga.tanggal_terbentuk.strftime('%Y-%m-%d') if lembaga.tanggal_terbentuk else None,
            'alamat_sekretariat': lembaga.alamat_sekretariat,
            'deskripsi': lembaga.deskripsi,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return handle_api_error(e, "api operation", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_lembaga_adat_create(request):
    """API untuk create lembaga adat"""
    try:
        # Gunakan request.POST dan request.FILES untuk form dengan file upload
        form = LembagaAdatForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                lembaga = form.save()
                logger.info(f"Lembaga adat created: {lembaga.id} - {lembaga.nama_lembaga}")
                return JsonResponse({
                    'success': True,
                    'message': 'Data lembaga adat berhasil ditambahkan',
                    'data': {
                        'id': lembaga.id,
                        'nama_lembaga': lembaga.nama_lembaga
                    }
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError as e:
        return handle_api_error(e, "parsing JSON data", logger)
    except ValidationError as e:
        return handle_api_error(e, "validating lembaga adat data", logger)
    except IntegrityError as e:
        return handle_api_error(e, "creating lembaga adat", logger)
    except Exception as e:
        return handle_api_error(e, "creating lembaga adat", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_lembaga_adat_update(request, pk):
    """API untuk update lembaga adat"""
    try:
        lembaga = get_object_or_404(LembagaAdat, pk=pk)
        
        # Gunakan request.POST dan request.FILES untuk form dengan file upload
        form = LembagaAdatForm(request.POST, request.FILES, instance=lembaga)
        if form.is_valid():
            lembaga = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data lembaga adat berhasil diperbarui',
                'data': {
                    'id': lembaga.id,
                    'nama_lembaga': lembaga.nama_lembaga
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError as e:
        return handle_api_error(e, "parsing lembaga adat update data", logger)
    except ObjectDoesNotExist as e:
        return handle_api_error(e, "finding lembaga adat to update", logger)
    except ValidationError as e:
        return handle_api_error(e, "validating lembaga adat data", logger)
    except IntegrityError as e:
        return handle_api_error(e, "updating lembaga adat", logger)
    except Exception as e:
        return handle_api_error(e, "updating lembaga adat", logger)


@csrf_protect
@require_http_methods(["DELETE"])
def api_lembaga_adat_delete(request, pk):
    """API untuk delete lembaga adat"""
    try:
        lembaga = get_object_or_404(LembagaAdat, pk=pk)
        nama = lembaga.nama_lembaga
        
        with transaction.atomic():
            lembaga.delete()
            logger.info(f"Lembaga adat deleted: {pk} - {nama}")
        
        return JsonResponse({
            'success': True,
            'message': f'Data lembaga adat {nama} berhasil dihapus'
        })
    except ObjectDoesNotExist as e:
        return handle_api_error(e, "finding lembaga adat to delete", logger)
    except IntegrityError as e:
        return handle_api_error(e, "deleting lembaga adat", logger)
    except Exception as e:
        return handle_api_error(e, "deleting lembaga adat", logger)


# Penggerak PKK API Views
@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_penggerak_pkk_list(request):
    """API untuk list penggerak PKK"""
    try:
        pkk_list = PenggerakPKK.objects.select_related('penduduk').all()
        
        # Search functionality
        search = request.GET.get('search', '')
        if search:
            pkk_list = pkk_list.filter(
                Q(penduduk__name__icontains=search) |
                Q(jabatan__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        paginator = Paginator(pkk_list, 10)
        page_obj = paginator.get_page(page)
        
        results = []
        for pkk in page_obj:
            results.append({
                'id': pkk.id,
                'penduduk_nama': pkk.penduduk.name,
                'penduduk_nik': pkk.penduduk.nik,
                'nama': pkk.penduduk.name,
                'nik': pkk.penduduk.nik,
                'jabatan': pkk.get_jabatan_display(),
                'jabatan_code': pkk.jabatan,
                'bidang_tugas': pkk.keahlian,
                'periode_mulai': pkk.tanggal_bergabung.strftime('%d/%m/%Y') if pkk.tanggal_bergabung else '',
                'periode_selesai': pkk.tanggal_keluar.strftime('%d/%m/%Y') if pkk.tanggal_keluar else None,
                'nomor_anggota': pkk.nomor_anggota,
                'keahlian': pkk.keahlian,
                'pengalaman_organisasi': pkk.pengalaman_organisasi,
                'prestasi': pkk.prestasi,
                'foto_profil': pkk.foto_profil.url if pkk.foto_profil else None,
                'kontak_whatsapp': pkk.kontak_whatsapp,
                'no_telepon': pkk.kontak_whatsapp,
                'alamat_lengkap': pkk.alamat_lengkap,
                'tanggal_bergabung': pkk.tanggal_bergabung.isoformat() if pkk.tanggal_bergabung else None,
                'tanggal_keluar': pkk.tanggal_keluar.isoformat() if pkk.tanggal_keluar else None,
                'status': pkk.get_status_display(),
                'status_code': pkk.status,
            })
        
        # Calculate statistics
        statistics = {
            'total': paginator.count,
            'aktif': pkk_list.filter(status='aktif').count(),
            'tidak_aktif': pkk_list.filter(status='tidak_aktif').count(),
            'cuti': pkk_list.filter(status='cuti').count(),
        }
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': paginator.count,
            'total_count': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'statistics': statistics,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving penggerak pkk list", logger)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_penggerak_pkk_detail(request, pk):
    """API untuk detail penggerak PKK"""
    try:
        pkk = get_object_or_404(PenggerakPKK, pk=pk)
        
        data = {
            'id': pkk.id,
            'penduduk_id': pkk.penduduk.id,
            'nama': pkk.penduduk.name,
            'nik': pkk.penduduk.nik,
            'jabatan': pkk.get_jabatan_display(),
            'jabatan_code': pkk.jabatan,
            'nomor_anggota': pkk.nomor_anggota,
            'keahlian': pkk.keahlian,
            'pengalaman_organisasi': pkk.pengalaman_organisasi,
            'prestasi': pkk.prestasi,
            'foto_profil': pkk.foto_profil.url if pkk.foto_profil else None,
            'kontak_whatsapp': pkk.kontak_whatsapp,
            'alamat_lengkap': pkk.alamat_lengkap,
            'tanggal_bergabung': pkk.tanggal_bergabung.isoformat() if pkk.tanggal_bergabung else None,
            'tanggal_keluar': pkk.tanggal_keluar.isoformat() if pkk.tanggal_keluar else None,
            'status': pkk.get_status_display(),
            'status_code': pkk.status,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except ObjectDoesNotExist as e:
        return handle_api_error(e, "finding penggerak pkk detail", logger)
    except Exception as e:
        return handle_api_error(e, "retrieving penggerak pkk detail", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_penggerak_pkk_create(request):
    """API untuk create penggerak PKK"""
    try:
        import json
        data = json.loads(request.body)
        
        form = PenggerakPKKForm(data)
        if form.is_valid():
            pkk = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data penggerak PKK berhasil ditambahkan',
                'data': {
                    'id': pkk.id,
                    'nama': pkk.penduduk.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return handle_api_error(e, "api operation", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_penggerak_pkk_update(request, pk):
    """API untuk update penggerak PKK"""
    try:
        import json
        pkk = get_object_or_404(PenggerakPKK, pk=pk)
        
        form = PenggerakPKKForm(request.POST, request.FILES, instance=pkk)
        if form.is_valid():
            pkk = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data penggerak PKK berhasil diperbarui',
                'data': {
                    'id': pkk.id,
                    'nama': pkk.penduduk.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return handle_api_error(e, "api operation", logger)


@csrf_protect
@require_http_methods(["DELETE"])
def api_penggerak_pkk_delete(request, pk):
    """API untuk delete penggerak PKK"""
    try:
        pkk = get_object_or_404(PenggerakPKK, pk=pk)
        nama = pkk.penduduk.name
        pkk.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data penggerak PKK {nama} berhasil dihapus'
        })
    except Exception as e:
        return handle_api_error(e, "api operation", logger)


# Kepemudaan API Views
@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_kepemudaan_list(request):
    """API untuk list kepemudaan"""
    try:
        kepemudaan_list = Kepemudaan.objects.select_related('ketua').all()
        
        # Search functionality
        search = request.GET.get('search', '')
        if search:
            kepemudaan_list = kepemudaan_list.filter(
                Q(nama_organisasi__icontains=search) |
                Q(ketua__name__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        paginator = Paginator(kepemudaan_list, 10)
        page_obj = paginator.get_page(page)
        
        results = []
        for kepemudaan in page_obj:
            results.append({
                'id': kepemudaan.id,
                'nama_organisasi': kepemudaan.nama_organisasi,
                'jenis_organisasi': kepemudaan.get_jenis_organisasi_display(),
                'jenis_code': kepemudaan.jenis_organisasi,
                'ketua_nama': kepemudaan.ketua.name if kepemudaan.ketua else None,
                'ketua_id': kepemudaan.ketua.id if kepemudaan.ketua else None,
                'deskripsi': kepemudaan.deskripsi,
                'kegiatan_rutin': kepemudaan.kegiatan_rutin,
                'jumlah_anggota': kepemudaan.jumlah_anggota_aktif,
                'alamat_sekretariat': kepemudaan.alamat_sekretariat,
                'kontak_phone': kepemudaan.kontak_phone,
                'foto_kegiatan': kepemudaan.foto_kegiatan.url if kepemudaan.foto_kegiatan else None,
                'tanggal_terbentuk': kepemudaan.tanggal_terbentuk.isoformat() if kepemudaan.tanggal_terbentuk else None,
                'status': kepemudaan.get_status_display(),
                'status_code': kepemudaan.status,
            })
        
        # Calculate statistics
        statistics = {
            'total': paginator.count,
            'aktif': kepemudaan_list.filter(status='aktif').count(),
            'non_aktif': kepemudaan_list.filter(status='non_aktif').count(),
            'alumni': kepemudaan_list.filter(status='alumni').count(),
        }
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': paginator.count,
            'total_count': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'statistics': statistics,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving kepemudaan list", logger)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_kepemudaan_detail(request, pk):
    """API untuk detail kepemudaan"""
    try:
        kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
        
        data = {
            'id': kepemudaan.id,
            'nama_organisasi': kepemudaan.nama_organisasi,
            'jenis_organisasi': kepemudaan.get_jenis_organisasi_display(),
            'jenis_code': kepemudaan.jenis_organisasi,
            'ketua_id': kepemudaan.ketua.id if kepemudaan.ketua else None,
            'ketua_nama': kepemudaan.ketua.name if kepemudaan.ketua else None,
            'deskripsi': kepemudaan.deskripsi,
            'kegiatan_rutin': kepemudaan.kegiatan_rutin,
            'jumlah_anggota': kepemudaan.jumlah_anggota,
            'jumlah_anggota_aktif': kepemudaan.jumlah_anggota_aktif,
            'alamat_sekretariat': kepemudaan.alamat_sekretariat,
            'kontak_phone': kepemudaan.kontak_phone,
            'foto_kegiatan': kepemudaan.foto_kegiatan.url if kepemudaan.foto_kegiatan else None,
            'tanggal_terbentuk': kepemudaan.tanggal_terbentuk.isoformat() if kepemudaan.tanggal_terbentuk else None,
            'status': kepemudaan.get_status_display(),
            'status_code': kepemudaan.status,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except ObjectDoesNotExist:
        return handle_api_error(ObjectDoesNotExist("Kepemudaan not found"), "retrieving kepemudaan detail", logger)
    except Exception as e:
        return handle_api_error(e, "retrieving kepemudaan detail", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_kepemudaan_create(request):
    """API untuk create kepemudaan"""
    try:
        import json
        data = json.loads(request.body)
        
        form = KepemudaanForm(data)
        if form.is_valid():
            kepemudaan = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data kepemudaan berhasil ditambahkan',
                'data': {
                    'id': kepemudaan.id,
                    'nama_organisasi': kepemudaan.nama_organisasi
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError:
        return handle_api_error(json.JSONDecodeError("Invalid JSON data"), "updating kepemudaan", logger)
    except ObjectDoesNotExist:
        return handle_api_error(ObjectDoesNotExist("Kepemudaan not found"), "updating kepemudaan", logger)
    except ValidationError as e:
        return handle_api_error(e, "updating kepemudaan", logger)
    except IntegrityError as e:
        return handle_api_error(e, "updating kepemudaan", logger)
    except Exception as e:
        return handle_api_error(e, "updating kepemudaan", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_kepemudaan_update(request, pk):
    """API untuk update kepemudaan"""
    try:
        kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
        
        form = KepemudaanForm(request.POST, request.FILES, instance=kepemudaan)
        if form.is_valid():
            kepemudaan = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data kepemudaan berhasil diperbarui',
                'data': {
                    'id': kepemudaan.id,
                    'nama_organisasi': kepemudaan.nama_organisasi
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except ObjectDoesNotExist:
        return handle_api_error(ObjectDoesNotExist("Kepemudaan not found"), "updating kepemudaan", logger)
    except Exception as e:
        return handle_api_error(e, "updating kepemudaan", logger)


@csrf_protect
@require_http_methods(["DELETE"])
def api_kepemudaan_delete(request, pk):
    """API untuk delete kepemudaan"""
    try:
        kepemudaan = get_object_or_404(Kepemudaan, pk=pk)
        nama = kepemudaan.nama_organisasi
        kepemudaan.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data kepemudaan {nama} berhasil dihapus'
        })
    except Exception as e:
        return handle_api_error(e, "retrieving karang taruna list", logger)


# Karang Taruna API Views
@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_karang_taruna_list(request):
    """API untuk list karang taruna"""
    try:
        karang_taruna_list = KarangTaruna.objects.select_related('penduduk').all()
        
        # Search functionality
        search = request.GET.get('search', '')
        if search:
            karang_taruna_list = karang_taruna_list.filter(
                Q(penduduk__name__icontains=search) |
                Q(jabatan__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        paginator = Paginator(karang_taruna_list, 10)
        page_obj = paginator.get_page(page)
        
        results = []
        for karang_taruna in page_obj:
            results.append({
                'id': karang_taruna.id,
                'penduduk_nama': karang_taruna.penduduk.name,
                'penduduk_nik': karang_taruna.penduduk.nik,
                'nama': karang_taruna.penduduk.name,
                'nik': karang_taruna.penduduk.nik,
                'nomor_anggota': karang_taruna.nomor_anggota,
                'jabatan': karang_taruna.get_jabatan_display(),
                'jabatan_code': karang_taruna.jabatan,
                'bidang_tugas': karang_taruna.bidang_keahlian,
                'periode_mulai': karang_taruna.tanggal_bergabung.strftime('%d/%m/%Y') if karang_taruna.tanggal_bergabung else '',
                'periode_selesai': karang_taruna.tanggal_keluar.strftime('%d/%m/%Y') if karang_taruna.tanggal_keluar else None,
                'keahlian': karang_taruna.bidang_keahlian,
                'pengalaman_organisasi': karang_taruna.pengalaman_organisasi,
                'prestasi': karang_taruna.prestasi_individu,
                'foto_profil': karang_taruna.foto_profil.url if karang_taruna.foto_profil else None,
                'kontak_whatsapp': karang_taruna.kontak_whatsapp,
                'no_telepon': karang_taruna.kontak_whatsapp,
                'alamat_lengkap': karang_taruna.alamat_lengkap,
                'tanggal_bergabung': karang_taruna.tanggal_bergabung.isoformat() if karang_taruna.tanggal_bergabung else None,
                'tanggal_keluar': karang_taruna.tanggal_keluar.isoformat() if karang_taruna.tanggal_keluar else None,
                'status': karang_taruna.get_status_display(),
                'status_code': karang_taruna.status,
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': paginator.count,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except ObjectDoesNotExist:
        return handle_api_error(ObjectDoesNotExist("Karang taruna not found"), "retrieving karang taruna detail", logger)
    except Exception as e:
        return handle_api_error(e, "retrieving karang taruna detail", logger)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def api_karang_taruna_detail(request, pk):
    """API untuk detail karang taruna"""
    try:
        karang_taruna = get_object_or_404(KarangTaruna, pk=pk)
        
        data = {
            'id': karang_taruna.id,
            'penduduk_id': karang_taruna.penduduk.id,
            'nama': karang_taruna.penduduk.name,
            'nik': karang_taruna.penduduk.nik,
            'nomor_anggota': karang_taruna.nomor_anggota,
            'jabatan': karang_taruna.get_jabatan_display(),
            'jabatan_code': karang_taruna.jabatan,
            'status': karang_taruna.get_status_display(),
            'status_code': karang_taruna.status,
            'tanggal_bergabung': karang_taruna.tanggal_bergabung.isoformat() if karang_taruna.tanggal_bergabung else None,
            'tanggal_keluar': karang_taruna.tanggal_keluar.isoformat() if karang_taruna.tanggal_keluar else None,
            'bidang_keahlian': karang_taruna.bidang_keahlian,
            'keahlian': karang_taruna.keahlian,
            'pengalaman_organisasi': karang_taruna.pengalaman_organisasi,
            'prestasi': karang_taruna.prestasi,
            'foto_profil': karang_taruna.foto_profil.url if karang_taruna.foto_profil else None,
            'kontak_whatsapp': karang_taruna.kontak_whatsapp,
            'alamat_lengkap': karang_taruna.alamat_lengkap,
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except json.JSONDecodeError:
        return handle_api_error(json.JSONDecodeError("Invalid JSON data"), "updating karang taruna", logger)
    except ObjectDoesNotExist:
        return handle_api_error(ObjectDoesNotExist("Karang taruna not found"), "updating karang taruna", logger)
    except ValidationError as e:
        return handle_api_error(e, "updating karang taruna", logger)
    except IntegrityError as e:
        return handle_api_error(e, "updating karang taruna", logger)
    except Exception as e:
        return handle_api_error(e, "updating karang taruna", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_karang_taruna_create(request):
    """API untuk create karang taruna"""
    try:
        data = json.loads(request.body)
        
        form = KarangTarunaForm(data)
        if form.is_valid():
            with transaction.atomic():
                karang_taruna = form.save()
                logger.info(f"Karang taruna created: {karang_taruna.id} - {karang_taruna.penduduk.name}")
                return JsonResponse({
                    'success': True,
                    'message': 'Data karang taruna berhasil ditambahkan',
                    'data': {
                        'id': karang_taruna.id,
                        'nama': karang_taruna.penduduk.name
                    }
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Validation failed',
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError as e:
        return handle_api_error(e, "parsing JSON data", logger)
    except ValidationError as e:
        return handle_api_error(e, "validating karang taruna data", logger)
    except IntegrityError as e:
        return handle_api_error(e, "creating karang taruna", logger)
    except Exception as e:
        return handle_api_error(e, "creating karang taruna", logger)


@csrf_protect
@require_http_methods(["POST"])
def api_karang_taruna_update(request, pk):
    """API untuk update karang taruna"""
    try:
        import json
        karang_taruna = get_object_or_404(KarangTaruna, pk=pk)
        
        form = KarangTarunaForm(request.POST, request.FILES, instance=karang_taruna)
        if form.is_valid():
            karang_taruna = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data karang taruna berhasil diperbarui',
                'data': {
                    'id': karang_taruna.id,
                    'nama': karang_taruna.penduduk.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except ObjectDoesNotExist:
        return handle_api_error(ObjectDoesNotExist("Karang taruna not found"), "updating karang taruna", logger)
    except Exception as e:
        return handle_api_error(e, "updating karang taruna", logger)


@csrf_protect
@require_http_methods(["DELETE"])
def api_karang_taruna_delete(request, pk):
    """API untuk delete karang taruna"""
    try:
        karang_taruna = get_object_or_404(KarangTaruna, pk=pk)
        nama = karang_taruna.penduduk.name
        karang_taruna.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data karang taruna {nama} berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)