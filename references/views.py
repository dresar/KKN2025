from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta, date
import json
import pandas as pd
import io
import traceback
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

from .models import Penduduk, Dusun, Lorong, DisabilitasType, DisabilitasData, ReligionReference, Family
from .forms import PendudukForm, DusunForm, LorongForm, DisabilitasTypeForm, DisabilitasDataForm, FamilyForm

# Test endpoint tanpa autentikasi untuk debugging
@csrf_exempt
def api_test_endpoint(request):
    """Test endpoint untuk memverifikasi routing API"""
    from datetime import datetime
    return JsonResponse({
        'status': 'success',
        'message': 'API routing berfungsi dengan baik',
        'method': request.method,
        'path': request.path,
        'timestamp': datetime.now().isoformat()
    })

# Consolidated API endpoints from former api_views.py
@csrf_exempt
@require_http_methods(["GET"])
def api_population(request):
    """API endpoint untuk data populasi (consolidated from api_views.py)"""
    try:
        populations = Penduduk.objects.all()
        
        # Search functionality
        search = request.GET.get('search', '')
        if search:
            populations = populations.filter(
                Q(name__icontains=search) |
                Q(nik__icontains=search) |
                Q(address__icontains=search)
            )
        
        # Filter by gender
        gender = request.GET.get('gender', '')
        if gender:
            populations = populations.filter(gender=gender)
        
        # Filter by dusun
        dusun_id = request.GET.get('dusun', '')
        if dusun_id:
            populations = populations.filter(dusun_id=dusun_id)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(populations, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for population in page_obj:
            results.append({
                'id': population.id,
                'name': population.name,
                'nik': population.nik,
                'gender': population.gender,
                'birth_date': population.birth_date.isoformat() if population.birth_date else None,
                'address': population.address,
                'dusun': population.dusun.name if population.dusun else None,
                'lorong': population.lorong.name if population.lorong else None,
                'phone': population.phone,
                'email': population.email,
                'is_active': population.is_active,
            })
        
        return JsonResponse({
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_population_stats(request):
    """API endpoint untuk statistik populasi"""
    try:
        total_population = Penduduk.objects.filter(is_active=True).count()
        male_count = Penduduk.objects.filter(gender='L', is_active=True).count()
        female_count = Penduduk.objects.filter(gender='P', is_active=True).count()
        
        # Age distribution
        from datetime import date
        today = date.today()
        age_groups = {
            '0-17': 0,
            '18-30': 0,
            '31-50': 0,
            '51+': 0
        }
        
        for person in Penduduk.objects.filter(is_active=True, birth_date__isnull=False):
            age = today.year - person.birth_date.year
            if age <= 17:
                age_groups['0-17'] += 1
            elif age <= 30:
                age_groups['18-30'] += 1
            elif age <= 50:
                age_groups['31-50'] += 1
            else:
                age_groups['51+'] += 1
        
        return JsonResponse({
            'total_population': total_population,
            'male_count': male_count,
            'female_count': female_count,
            'age_distribution': age_groups,
            'dusun_distribution': list(Dusun.objects.annotate(
                population_count=Count('penduduk')
            ).values('name', 'population_count'))
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_population_export(request):
    """API endpoint untuk export data populasi"""
    try:
        populations = Penduduk.objects.filter(is_active=True)
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="population_data.csv"'
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Nama', 'NIK', 'Jenis Kelamin', 'Tanggal Lahir', 'Alamat', 'Dusun', 'Lorong', 'Telepon', 'Email'])
        
        # Write data
        for pop in populations:
            writer.writerow([
                pop.id,
                pop.name,
                pop.nik,
                pop.get_gender_display(),
                pop.birth_date.strftime('%Y-%m-%d') if pop.birth_date else '',
                pop.address,
                pop.dusun.name if pop.dusun else '',
                pop.lorong.name if pop.lorong else '',
                pop.phone or '',
                pop.email or ''
            ])
        
        response.write(output.getvalue())
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_dusun(request):
    """API endpoint untuk data dusun"""
    try:
        dusuns = Dusun.objects.filter(is_active=True)
        
        # Search functionality
        search = request.GET.get('search', '')
        if search:
            dusuns = dusuns.filter(Q(name__icontains=search) | Q(code__icontains=search))
        
        results = []
        for dusun in dusuns:
            results.append({
                'id': dusun.id,
                'name': dusun.name,
                'code': dusun.code,
                'description': dusun.description,
                'population_count': dusun.penduduk_set.filter(is_active=True).count(),
                'is_active': dusun.is_active,
            })
        
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_disability(request):
    """API endpoint untuk data disabilitas"""
    try:
        disabilities = DisabilitasData.objects.filter(is_active=True)
        
        # Search functionality
        search = request.GET.get('search', '')
        if search:
            disabilities = disabilities.filter(
                Q(penduduk__name__icontains=search) |
                Q(disability_type__name__icontains=search)
            )
        
        results = []
        for disability in disabilities:
            results.append({
                'id': disability.id,
                'penduduk_name': disability.penduduk.name,
                'penduduk_nik': disability.penduduk.nik,
                'disability_type': disability.disability_type.name,
                'severity_level': disability.severity_level,
                'description': disability.description,
                'is_active': disability.is_active,
            })
        
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def public_stats_api(request):
    """Public statistics API endpoint tanpa autentikasi untuk testing"""
    try:
        # Basic statistics without authentication
        total_penduduk = Penduduk.objects.count()
        total_dusun = Dusun.objects.count()
        total_lorong = Lorong.objects.count()
        
        data = {
            'status': 'success',
            'message': 'Public API berhasil diakses',
            'data': {
                'total_penduduk': total_penduduk,
                'total_dusun': total_dusun,
                'total_lorong': total_lorong,
                'timestamp': timezone.now().isoformat()
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def public_dusun_list_api(request):
    """Public API endpoint for dusun list without authentication"""
    try:
        per_page = int(request.GET.get('per_page', 100))
        
        queryset = Dusun.objects.filter(is_active=True).order_by('name')
        
        # Apply pagination if needed
        if per_page > 0:
            queryset = queryset[:per_page]
        
        data = {
            'results': [
                {
                    'id': d.id,
                    'name': d.name,
                    'code': d.code,
                    'description': d.description
                }
                for d in queryset
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def public_lorong_list_api(request):
    """Public API endpoint for lorong list without authentication"""
    try:
        per_page = int(request.GET.get('per_page', 100))
        dusun_id = request.GET.get('dusun', '')
        
        queryset = Lorong.objects.filter(is_active=True)
        
        if dusun_id:
            queryset = queryset.filter(dusun_id=dusun_id)
            
        queryset = queryset.order_by('name')
        
        # Apply pagination if needed
        if per_page > 0:
            queryset = queryset[:per_page]
        
        data = {
            'results': [
                {
                    'id': l.id,
                    'name': l.name,
                    'code': l.code,
                    'description': l.description,
                    'dusun_id': l.dusun.id if l.dusun else None,
                    'dusun_name': l.dusun.name if l.dusun else None
                }
                for l in queryset
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def public_penduduk_list_api(request):
    """Public API endpoint for penduduk list without authentication"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        dusun_id = request.GET.get('dusun', '')
        
        queryset = Penduduk.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(nik__icontains=search) |
                Q(birth_place__icontains=search)
            )
            
        if dusun_id:
            queryset = queryset.filter(dusun_id=dusun_id)
        
        queryset = queryset.order_by('-created_at')
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': p.id,
                    'name': p.name,
                    'nik': p.nik,
                    'kk_number': p.kk_number,
                    'gender': p.get_gender_display(),
                    'birth_place': p.birth_place,
                    'birth_date': p.birth_date.strftime('%d/%m/%Y') if p.birth_date else '',
                    'dusun': p.dusun.name if p.dusun else '',
                    'lorong': p.lorong.name if p.lorong else '',
                    'address': p.address,
                    'is_active': p.is_active
                }
                for p in page_obj
            ],
            'page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def public_penduduk_create_api(request):
    """Public API endpoint for creating penduduk without authentication"""
    try:
        # Handle both JSON and FormData
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Handle FormData from HTML form
            data = request.POST.dict()
        
        # Map frontend field names to backend field names
        field_mapping = {
            'name': 'name',
            'nama_lengkap': 'name',
            'jenis_kelamin': 'gender',
            'tempat_lahir': 'birth_place',
            'tanggal_lahir': 'birth_date',
            'agama': 'religion',
            'no_kk': 'kk_number',
            'kepala_keluarga': 'family_head',
            'hubungan_keluarga': 'relationship_to_head',
            'status_perkawinan': 'marital_status',
            'rt': 'rt_number',
            'rw': 'rw_number',
            'no_rumah': 'house_number',
            'kode_pos': 'postal_code',
            'alamat_lengkap': 'address',
            'pendidikan': 'education',
            'pekerjaan': 'occupation',
            'golongan_darah': 'blood_type',
            'tinggi_badan': 'height',
            'berat_badan': 'weight',
            'kewarganegaraan': 'citizenship',
            'no_telepon': 'phone_number',
            'no_hp': 'mobile_number',
            'kontak_darurat': 'emergency_contact',
            'no_kontak_darurat': 'emergency_phone'
        }
        
        # Map the data to correct field names
        mapped_data = {}
        for frontend_field, backend_field in field_mapping.items():
            if frontend_field in data and data[frontend_field]:
                mapped_data[backend_field] = data[frontend_field]
        
        # Add fields that don't need mapping
        direct_fields = ['nik', 'birth_place', 'birth_date', 'religion', 'kk_number', 
                        'family_head', 'relationship_to_head', 'marital_status', 'dusun', 
                        'lorong', 'rt_number', 'rw_number', 'house_number', 'postal_code', 
                        'address', 'education', 'occupation', 'blood_type', 'height', 
                        'weight', 'citizenship', 'phone_number', 'mobile_number', 'email',
                        'emergency_contact', 'emergency_phone', 'emergency_relationship', 'passport_number',
                        'passport_expiry_date', 'is_alive', 'death_date', 'death_cause', 'is_active']
        
        for field in direct_fields:
            if field in data and data[field]:
                mapped_data[field] = data[field]
            
        # Use form validation
        form = PendudukForm(mapped_data)
        
        if form.is_valid():
            penduduk = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data penduduk berhasil ditambahkan',
                'data': {
                    'id': penduduk.id,
                    'name': penduduk.name,
                    'nik': penduduk.nik,
                    'age': penduduk.age,
                    'dusun_name': penduduk.dusun.name if penduduk.dusun else None
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
def public_penduduk_detail_api(request, penduduk_id):
    """Public API endpoint for retrieving individual penduduk data without authentication"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        penduduk = Penduduk.objects.get(id=penduduk_id)
        
        data = {
            'id': penduduk.id,
            'nik': penduduk.nik,
            'kk_number': penduduk.kk_number,
            'name': penduduk.name,
            'gender': penduduk.gender,
            'birth_place': penduduk.birth_place,
            'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else None,
            'religion': penduduk.religion,
            'marital_status': penduduk.marital_status,
            'citizenship': penduduk.citizenship,
            'dusun_id': penduduk.dusun.id if penduduk.dusun else None,
            'dusun_name': penduduk.dusun.name if penduduk.dusun else None,
            'lorong_id': penduduk.lorong.id if penduduk.lorong else None,
            'lorong_name': penduduk.lorong.name if penduduk.lorong else None,
            'rt_number': penduduk.rt_number,
            'rw_number': penduduk.rw_number,
            'address': penduduk.address,
            'education': penduduk.education,
            'occupation': penduduk.occupation,
            'blood_type': penduduk.blood_type,
            'phone_number': penduduk.phone_number,
            'mobile_number': penduduk.mobile_number,
            'email': penduduk.email,
            'is_active': penduduk.is_active,
        }
        
        return JsonResponse(data)
        
    except Penduduk.DoesNotExist:
        return JsonResponse({'error': 'Penduduk not found'}, status=404)
    except Exception as e:
        print(f"ERROR in penduduk_detail_api: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def public_penduduk_update_api(request, penduduk_id):
    """Public API endpoint for updating penduduk data without authentication"""
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        penduduk = Penduduk.objects.get(id=penduduk_id)
        data = json.loads(request.body)
        
        # Map frontend field names to backend field names
        field_mapping = {
            'name': 'name',
            'nama_lengkap': 'name',
            'jenis_kelamin': 'gender',
            'tempat_lahir': 'birth_place',
            'tanggal_lahir': 'birth_date',
            'agama': 'religion',
            'no_kk': 'kk_number',
            'kepala_keluarga': 'family_head',
            'hubungan_keluarga': 'relationship_to_head',
            'status_perkawinan': 'marital_status',
            'rt': 'rt_number',
            'rw': 'rw_number',
            'no_rumah': 'house_number',
            'kode_pos': 'postal_code',
            'alamat_lengkap': 'address',
            'pendidikan': 'education',
            'pekerjaan': 'occupation',
            'golongan_darah': 'blood_type',
            'tinggi_badan': 'height',
            'berat_badan': 'weight',
            'kewarganegaraan': 'citizenship',
            'no_telepon': 'phone_number',
            'no_hp': 'mobile_number',
            'kontak_darurat': 'emergency_contact',
            'no_kontak_darurat': 'emergency_phone'
        }
        
        # Map the data to correct field names
        mapped_data = {}
        for frontend_field, backend_field in field_mapping.items():
            if frontend_field in data and data[frontend_field] is not None:
                mapped_data[backend_field] = data[frontend_field]
        
        # Add fields that don't need mapping
        direct_fields = ['nik', 'birth_place', 'birth_date', 'religion', 'kk_number', 
                        'family_head', 'relationship_to_head', 'marital_status', 'dusun', 
                        'lorong', 'rt_number', 'rw_number', 'house_number', 'postal_code', 
                        'address', 'education', 'occupation', 'blood_type', 'height', 
                        'weight', 'citizenship', 'phone_number', 'mobile_number', 'email',
                        'emergency_contact', 'emergency_phone', 'emergency_relationship', 'emergency_contact_name', 'emergency_contact_phone', 'passport_number',
                        'passport_expiry_date', 'is_alive', 'death_date', 'death_cause', 'is_active', 'gender']
        
        for field in direct_fields:
            if field in data and data[field] is not None:
                mapped_data[field] = data[field]
        
        # Create form instance with data and existing instance
        form = PendudukForm(mapped_data, instance=penduduk)
        
        if form.is_valid():
            updated_penduduk = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data penduduk berhasil diperbarui',
                'data': {
                    'id': updated_penduduk.id,
                    'name': updated_penduduk.name,
                    'nik': updated_penduduk.nik
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except Penduduk.DoesNotExist:
        return JsonResponse({'error': 'Penduduk not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def references_admin(request):
    """Main references admin view"""
    context = {
        'page_title': 'Data Referensi',
        'page_subtitle': 'Kelola data penduduk dan referensi desa'
    }
    return render(request, 'admin/modules/references/index.html', context)

# Penduduk Views
@csrf_exempt
def penduduk_list_api(request):
    """API endpoint for penduduk list with pagination and search"""
    try:
        # Handle page parameter safely
        page_param = request.GET.get('page', '1')
        if page_param == 'undefined' or not page_param:
            page_param = '1'
        page = int(page_param)
        
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        dusun_id = request.GET.get('dusun', '')
        
        queryset = Penduduk.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(nik__icontains=search) |
                Q(birth_place__icontains=search)
            )
            
        if dusun_id:
            queryset = queryset.filter(dusun_id=dusun_id)
        
        queryset = queryset.order_by('-created_at')
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': p.id,
                    'name': p.name,
                    'nik': p.nik,
                    'kk_number': p.kk_number,
                    'gender': p.get_gender_display(),
                    'birth_place': p.birth_place,
                    'birth_date': p.birth_date.strftime('%d/%m/%Y') if p.birth_date else '',
                    'dusun': p.dusun.name if p.dusun else '',
                    'lorong': p.lorong.name if p.lorong else '',
                    'marital_status': p.get_marital_status_display(),
                    'religion': p.religion,
                    'age': p.age,
                    'phone_number': p.phone_number,
                    'mobile_number': p.mobile_number,
                    'is_active': p.is_active,
                    'created_at': p.created_at.strftime('%d/%m/%Y %H:%M') if hasattr(p, 'created_at') else ''
                } for p in page_obj
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        print(f"ERROR in penduduk_detail_api: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)


# Admin Views
@login_required
@user_passes_test(is_admin)
def dusun_admin(request):
    """Dusun admin view"""
    # Handle search
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    
    # Get dusun data
    dusun_list = Dusun.objects.all().order_by('name')
    
    if search:
        dusun_list = dusun_list.filter(
            Q(name__icontains=search) | Q(code__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(dusun_list, 10)
    dusun_page = paginator.get_page(page)
    
    context = {
        'page_title': 'Kelola Dusun',
        'page_subtitle': 'Kelola data dusun',
        'dusun_list': dusun_page,
        'search': search,
        'paginator': paginator
    }
    return render(request, 'admin/modules/references/dusun.html', context)

@login_required
@user_passes_test(is_admin)
def lorong_admin(request):
    """Lorong admin view"""
    context = {
        'page_title': 'Kelola Lorong',
        'page_subtitle': 'Kelola data lorong'
    }
    return render(request, 'admin/modules/references/lorong.html', context)

@login_required
@user_passes_test(is_admin)
def penduduk_admin(request):
    """Penduduk admin view"""
    context = {
        'page_title': 'Kelola Penduduk',
        'page_subtitle': 'Kelola data penduduk'
    }
    return render(request, 'admin/modules/references/penduduk.html', context)

@login_required
@user_passes_test(is_admin)
def disabilitas_admin(request):
    """Disabilitas admin view"""
    context = {
        'page_title': 'Kelola Disabilitas',
        'page_subtitle': 'Kelola data disabilitas'
    }
    return render(request, 'admin/modules/references/disabilitas.html', context)

# Statistics API
@csrf_exempt
def references_stats_api(request):
    """API for references statistics"""
    try:
        from django.db.models import Count, Q
        from datetime import datetime, timedelta
        
        # Basic stats
        total_penduduk = Penduduk.objects.count()
        total_dusun = Dusun.objects.count()
        total_lorong = Lorong.objects.count()
        total_disabilitas = DisabilitasData.objects.count()
        
        # Demographics
        male_count = Penduduk.objects.filter(gender='L').count()
        female_count = Penduduk.objects.filter(gender='P').count()
        
        # Age groups calculation
        from datetime import date
        today = date.today()
        
        anak_count = 0
        dewasa_count = 0
        lansia_count = 0
        
        for penduduk in Penduduk.objects.all():
            age = today.year - penduduk.birth_date.year - ((today.month, today.day) < (penduduk.birth_date.month, penduduk.birth_date.day))
            if age < 18:
                anak_count += 1
            elif age < 60:
                dewasa_count += 1
            else:
                lansia_count += 1
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_penduduk = Penduduk.objects.filter(created_at__gte=thirty_days_ago).count()
        new_disabilitas = DisabilitasData.objects.filter(created_at__gte=thirty_days_ago).count()
        
        # Population by dusun
        population_by_dusun = list(Penduduk.objects.values('dusun__name').annotate(count=Count('id')).order_by('-count'))
        
        # Disability by type
        disability_by_type = list(DisabilitasData.objects.values('disability_type__name').annotate(count=Count('id')).order_by('-count'))
        
        # Religion distribution
        religion_distribution = list(Penduduk.objects.values('religion').annotate(count=Count('id')).order_by('-count'))
        
        # Education distribution
        education_distribution = list(Penduduk.objects.values('education').annotate(count=Count('id')).order_by('-count'))
        
        stats = {
            'basic_stats': {
                'total_penduduk': total_penduduk,
                'total_dusun': total_dusun,
                'total_lorong': total_lorong,
                'total_disabilitas': total_disabilitas
            },
            'demographics': {
                'male_count': male_count,
                'female_count': female_count,
                'age_groups': {
                    'anak': anak_count,
                    'dewasa': dewasa_count,
                    'lansia': lansia_count
                }
            },
            'recent_activity': {
                'new_penduduk': new_penduduk,
                'new_disabilitas': new_disabilitas
            },
            'population_by_dusun': population_by_dusun,
            'disability': {
                'by_type': disability_by_type
            },
            'distributions': {
                'religion': religion_distribution,
                'education': education_distribution
            }
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Export/Import APIs (placeholder)
@login_required
@user_passes_test(is_admin)
def export_data(request, model_type):
    """Export data API"""
    return JsonResponse({'message': f'Export {model_type} not implemented yet'})

@login_required
@user_passes_test(is_admin)
def import_data(request, model_type):
    """Import data API"""
    return JsonResponse({'message': f'Import {model_type} not implemented yet'})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def penduduk_create_api(request):
    """Enhanced API endpoint for creating penduduk with better validation"""
    if request.method == 'GET':
        # Return form data and choices
        try:
            dusun_list = [{'id': d.id, 'name': d.name} for d in Dusun.objects.filter(is_active=True).order_by('name')]
            lorong_list = [{'id': l.id, 'name': l.name, 'dusun_id': l.dusun.id} for l in Lorong.objects.filter(is_active=True).order_by('name')]
            family_heads = [{'id': p.id, 'name': p.name, 'nik': p.nik} for p in Penduduk.objects.filter(is_active=True, family_head__isnull=True).order_by('name')]
            
            return JsonResponse({
                'success': True,
                'data': {
                    'dusun_choices': dusun_list,
                    'lorong_choices': lorong_list,
                    'family_head_choices': family_heads,
                    'religion_choices': [{'value': k, 'label': v} for k, v in Penduduk.RELIGION_CHOICES],
                    'gender_choices': [{'value': k, 'label': v} for k, v in Penduduk.GENDER_CHOICES],
                    'marital_status_choices': [{'value': k, 'label': v} for k, v in Penduduk.MARITAL_STATUS_CHOICES],
                    'education_choices': [{'value': k, 'label': v} for k, v in Penduduk.EDUCATION_CHOICES],
                    'blood_type_choices': [{'value': k, 'label': v} for k, v in Penduduk.BLOOD_TYPE_CHOICES],
                    'citizenship_choices': [{'value': k, 'label': v} for k, v in Penduduk.CITIZENSHIP_CHOICES]
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    try:
        data = json.loads(request.body)
        
        # Use form validation instead of manual validation
        form = PendudukForm(data)
        
        if form.is_valid():
            penduduk = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data penduduk berhasil ditambahkan',
                'data': {
                    'id': penduduk.id,
                    'name': penduduk.name,
                    'nik': penduduk.nik,
                    'age': penduduk.age,
                    'dusun_name': penduduk.dusun.name if penduduk.dusun else None
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def penduduk_detail_api(request, pk):
    """API endpoint for penduduk detail, update, and delete"""
    try:
        penduduk = get_object_or_404(Penduduk, pk=pk)
        
        if request.method == 'GET':
            # Calculate age
            age = None
            if penduduk.birth_date:
                today = date.today()
                age = today.year - penduduk.birth_date.year - ((today.month, today.day) < (penduduk.birth_date.month, penduduk.birth_date.day))
            
            # Get display values for choice fields
            gender_display = dict(Penduduk.GENDER_CHOICES).get(penduduk.gender, '') if penduduk.gender else ''
            religion_display = dict(Penduduk.RELIGION_CHOICES).get(penduduk.religion, '') if penduduk.religion else ''
            marital_status_display = dict(Penduduk.MARITAL_STATUS_CHOICES).get(penduduk.marital_status, '') if penduduk.marital_status else ''
            education_display = dict(Penduduk.EDUCATION_CHOICES).get(penduduk.education, '') if penduduk.education else ''
            blood_type_display = dict(Penduduk.BLOOD_TYPE_CHOICES).get(penduduk.blood_type, '') if penduduk.blood_type else ''
            citizenship_display = dict(Penduduk.CITIZENSHIP_CHOICES).get(penduduk.citizenship, '') if penduduk.citizenship else ''
            
            # Get family members (same KK number)
            family_members = []
            if penduduk.kk_number:
                family_queryset = Penduduk.objects.filter(kk_number=penduduk.kk_number).exclude(id=penduduk.id)
                for member in family_queryset:
                    member_age = None
                    if member.birth_date:
                        today = date.today()
                        member_age = today.year - member.birth_date.year - ((today.month, today.day) < (member.birth_date.month, member.birth_date.day))
                    
                    family_members.append({
                        'id': member.id,
                        'name': member.name,
                        'nik': member.nik,
                        'relationship': member.relationship_to_head,
                        'age': member_age
                    })
            
            data = {
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik,
                'kk_number': penduduk.kk_number,
                'gender': penduduk.gender,
                'gender_display': gender_display,
                'birth_place': penduduk.birth_place,
                'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else '',
                'age': age,
                'dusun': penduduk.dusun.id if penduduk.dusun else None,
                'dusun_name': penduduk.dusun.name if penduduk.dusun else None,
                'lorong': penduduk.lorong.id if penduduk.lorong else None,
                'lorong_name': penduduk.lorong.name if penduduk.lorong else None,
                'marital_status': penduduk.marital_status,
                'marital_status_display': marital_status_display,
                'religion': penduduk.religion,
                'religion_display': religion_display,
                'education': penduduk.education,
                'education_display': education_display,
                'occupation': penduduk.occupation,
                'address': penduduk.address,
                'rt': penduduk.rt_number,
                'rw': penduduk.rw_number,
                'postal_code': penduduk.postal_code,
                'phone': penduduk.phone_number,
                'mobile_phone': penduduk.mobile_number,
                'email': penduduk.email,
                'emergency_contact': penduduk.emergency_contact,
                'blood_type': penduduk.blood_type,
                'blood_type_display': blood_type_display,
                'height': penduduk.height,
                'weight': penduduk.weight,
                'is_active': penduduk.is_active,
                'citizenship': penduduk.citizenship,
                'citizenship_display': citizenship_display,
                'passport_number': penduduk.passport_number,
                'family_head': penduduk.family_head.id if penduduk.family_head else None,
                'family_position': penduduk.relationship_to_head,
                'family_members': family_members
            }
            return JsonResponse(data)
        
        elif request.method == 'PUT':
            try:
                data = json.loads(request.body)
                
                # Use form validation for update
                form = PendudukForm(data, instance=penduduk)
                
                if form.is_valid():
                    updated_penduduk = form.save()
                    return JsonResponse({
                        'success': True,
                        'message': 'Data penduduk berhasil diperbarui',
                        'data': {
                            'id': updated_penduduk.id,
                            'name': updated_penduduk.name,
                            'nik': updated_penduduk.nik,
                            'age': (date.today() - updated_penduduk.birth_date).days // 365 if updated_penduduk.birth_date else None,
                            'dusun_name': updated_penduduk.dusun.name if updated_penduduk.dusun else None
                        }
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'errors': form.errors
                    }, status=400)
            except json.JSONDecodeError:
                return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
        
        elif request.method == 'DELETE':
            penduduk.delete()
            return JsonResponse({
                'success': True,
                'message': 'Data penduduk berhasil dihapus'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def penduduk_bulk_delete_api(request):
    """API endpoint for bulk delete penduduk"""
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({
                'success': False,
                'error': 'No IDs provided'
            }, status=400)
        
        deleted_count = Penduduk.objects.filter(id__in=ids).delete()[0]
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} data penduduk berhasil dihapus',
            'deleted_count': deleted_count
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def penduduk_search_api(request):
    """Enhanced search API for penduduk with advanced filters"""
    try:
        # Get search parameters
        search = request.GET.get('search', '')
        dusun_id = request.GET.get('dusun', '')
        lorong_id = request.GET.get('lorong', '')
        gender = request.GET.get('gender', '')
        marital_status = request.GET.get('marital_status', '')
        age_min = request.GET.get('age_min', '')
        age_max = request.GET.get('age_max', '')
        is_active = request.GET.get('is_active', 'true')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Base queryset
        queryset = Penduduk.objects.all()
        
        # Apply filters
        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(nik__icontains=search) |
                Q(kk_number__icontains=search) |
                Q(address__icontains=search)
            )
        
        if dusun_id:
            queryset = queryset.filter(dusun_id=dusun_id)
        
        if lorong_id:
            queryset = queryset.filter(lorong_id=lorong_id)
        
        if gender:
            queryset = queryset.filter(gender=gender)
        
        if marital_status:
            queryset = queryset.filter(marital_status=marital_status)
        
        # Age filtering (requires calculation)
        if age_min or age_max:
            from datetime import date
            today = date.today()
            
            if age_min:
                birth_year_max = today.year - int(age_min)
                queryset = queryset.filter(birth_date__year__lte=birth_year_max)
            
            if age_max:
                birth_year_min = today.year - int(age_max)
                queryset = queryset.filter(birth_date__year__gte=birth_year_min)
        
        # Order by name
        queryset = queryset.order_by('name')
        
        # Pagination
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize results
        results = []
        for penduduk in page_obj:
            age = penduduk.age if hasattr(penduduk, 'age') else None
            results.append({
                'id': penduduk.id,
                'name': penduduk.name,
                'nik': penduduk.nik,
                'kk_number': penduduk.kk_number,
                'gender': penduduk.gender,
                'gender_display': dict(Penduduk.GENDER_CHOICES).get(penduduk.gender, ''),
                'age': age,
                'dusun_name': penduduk.dusun.name if penduduk.dusun else '',
                'lorong_name': penduduk.lorong.name if penduduk.lorong else '',
                'address': penduduk.address,
                'phone_number': penduduk.phone_number,
                'mobile_number': penduduk.mobile_number,
                'is_active': penduduk.is_active,
                'marital_status_display': dict(Penduduk.MARITAL_STATUS_CHOICES).get(penduduk.marital_status, '')
            })
        
        return JsonResponse({
            'success': True,
            'results': results,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def penduduk_export_api(request):
    """API endpoint for exporting penduduk data"""
    try:
        format_type = request.GET.get('format', 'excel')  # excel, csv, json
        
        # Get filtered data (reuse search logic)
        search = request.GET.get('search', '')
        dusun_id = request.GET.get('dusun', '')
        
        queryset = Penduduk.objects.filter(is_active=True)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(nik__icontains=search) |
                Q(kk_number__icontains=search)
            )
        
        if dusun_id:
            queryset = queryset.filter(dusun_id=dusun_id)
        
        queryset = queryset.order_by('name')
        
        if format_type == 'json':
            data = []
            for penduduk in queryset:
                data.append({
                    'id': penduduk.id,
                    'name': penduduk.name,
                    'nik': penduduk.nik,
                    'kk_number': penduduk.kk_number,
                    'gender': dict(Penduduk.GENDER_CHOICES).get(penduduk.gender, ''),
                    'birth_place': penduduk.birth_place,
                    'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else '',
                    'age': penduduk.age,
                    'dusun': penduduk.dusun.name if penduduk.dusun else '',
                    'lorong': penduduk.lorong.name if penduduk.lorong else '',
                    'address': penduduk.address,
                    'phone_number': penduduk.phone_number,
                    'religion': dict(Penduduk.RELIGION_CHOICES).get(penduduk.religion, ''),
                    'marital_status': dict(Penduduk.MARITAL_STATUS_CHOICES).get(penduduk.marital_status, ''),
                    'education': dict(Penduduk.EDUCATION_CHOICES).get(penduduk.education, ''),
                    'occupation': penduduk.occupation
                })
            
            return JsonResponse({
                'success': True,
                'data': data,
                'total_records': len(data)
            })
        
        else:
            # For Excel/CSV, return download URL or file
            return JsonResponse({
                'success': True,
                'message': 'Export functionality available',
                'download_url': f'/admin/references/export/penduduk/?format={format_type}'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Dusun Views
@csrf_exempt
def dusun_list_api(request):
    """API endpoint for dusun list with pagination and search - accessible for admin panel"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        
        queryset = Dusun.objects.all()
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        queryset = queryset.order_by('name')
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': d.id,
                    'name': d.name,
                    'code': d.code,
                    'population_count': d.population_count,
                    'area_size': float(d.area_size) if d.area_size else 0,
                    'total_residents': d.residents.count(),
                    'is_active': d.is_active
                } for d in page_obj
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def dusun_create_api(request):
    """API endpoint for creating dusun"""
    try:
        # Handle both JSON and FormData
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Handle FormData from HTML form
            data = request.POST.dict()
            
        form = DusunForm(data)
        
        if form.is_valid():
            dusun = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data dusun berhasil ditambahkan',
                'data': {
                    'id': dusun.id,
                    'name': dusun.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def dusun_detail_api(request, pk):
    """API endpoint for dusun detail, update, and delete"""
    try:
        dusun = get_object_or_404(Dusun, pk=pk)
        
        if request.method == 'GET':
            data = {
                'id': dusun.id,
                'name': dusun.name,
                'code': dusun.code,
                'description': dusun.description,
                'area_size': float(dusun.area_size) if dusun.area_size else 0,
                'population_count': dusun.population_count,
                'is_active': dusun.is_active
            }
            return JsonResponse(data)
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            form = DusunForm(data, instance=dusun)
            
            if form.is_valid():
                dusun = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Data dusun berhasil diperbarui'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        
        elif request.method == 'DELETE':
            # Check if dusun has penduduk
            if dusun.residents.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Tidak dapat menghapus dusun yang masih memiliki penduduk'
                }, status=400)
            
            dusun.delete()
            return JsonResponse({
                'success': True,
                'message': 'Data dusun berhasil dihapus'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Lorong Views
@csrf_exempt
def lorong_list_api(request):
    """API endpoint for lorong list with pagination and search"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        dusun_id = request.GET.get('dusun_id')
        
        queryset = Lorong.objects.all()
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        if dusun_id:
            queryset = queryset.filter(dusun_id=dusun_id)
        
        queryset = queryset.select_related('dusun').order_by('dusun__name', 'name')
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': l.id,
                    'name': l.name,
                    'code': l.code,
                    'dusun': l.dusun.name if l.dusun else '',
                    'dusun_id': l.dusun.id if l.dusun else None,
                    'length': float(l.length) if l.length else 0,
                    'house_count': l.house_count,
                    'total_residents': l.residents.count(),
                    'is_active': l.is_active
                } for l in page_obj
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def lorong_create_api(request):
    """API endpoint for creating lorong"""
    if request.method == 'GET':
        # Return dusun choices for form
        dusun_list = [{'id': d.id, 'name': d.name} for d in Dusun.objects.all()]
        return JsonResponse({'dusun_choices': dusun_list})
    
    try:
        # Handle both JSON and FormData
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Handle FormData
            data = request.POST.dict()
        
        form = LorongForm(data)
        
        if form.is_valid():
            lorong = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data lorong berhasil ditambahkan',
                'data': {
                    'id': lorong.id,
                    'name': lorong.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "PUT", "DELETE"])
def lorong_detail_api(request, pk):
    """API endpoint for lorong detail, update, and delete"""
    try:
        lorong = get_object_or_404(Lorong, pk=pk)
        
        if request.method == 'GET':
            data = {
                'id': lorong.id,
                'name': lorong.name,
                'code': lorong.code,
                'description': lorong.description,
                'length': float(lorong.length) if lorong.length else 0,
                'house_count': lorong.house_count,
                'dusun_id': lorong.dusun.id if lorong.dusun else None,
                'is_active': lorong.is_active
            }
            return JsonResponse(data)
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            form = LorongForm(data, instance=lorong)
            
            if form.is_valid():
                lorong = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Data lorong berhasil diperbarui'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        
        elif request.method == 'DELETE':
            # Delete all penduduk associated with this lorong first
            if lorong.residents.exists():
                deleted_count = lorong.residents.count()
                lorong.residents.all().delete()
                
            lorong.delete()
            return JsonResponse({
                'success': True,
                'message': f'Data lorong berhasil dihapus{f" beserta {deleted_count} data penduduk" if "deleted_count" in locals() else ""}'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Statistics API
@login_required
@user_passes_test(is_admin)
def penduduk_count_api(request):
    """API endpoint for getting total penduduk count"""
    try:
        total_count = Penduduk.objects.filter(is_active=True).count()
        return JsonResponse({
            'total_count': total_count,
            'year': date.today().year
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Duplicate references_stats_api removed - keeping only the first definition

# Disabilitas Type Views
@csrf_exempt
def disabilitas_type_list_api(request):
    """API endpoint for disabilitas type list"""
    try:
        search = request.GET.get('search', '').strip()
        
        queryset = DisabilitasType.objects.all()
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        queryset = queryset.order_by('name')
        
        data = {
            'results': [
                {
                    'id': dt.id,
                    'name': dt.name,
                    'code': dt.code,
                    'description': dt.description,
                    'is_active': dt.is_active,
                    'total_cases': DisabilitasData.objects.filter(disability_type=dt).count()
                } for dt in queryset
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def disabilitas_type_create_api(request):
    """API endpoint for creating disabilitas type"""
    try:
        data = json.loads(request.body)
        form = DisabilitasTypeForm(data)
        
        if form.is_valid():
            disability_type = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Jenis disabilitas berhasil ditambahkan',
                'data': {
                    'id': disability_type.id,
                    'name': disability_type.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "PUT", "DELETE"])
def disabilitas_type_detail_api(request, pk):
    """API endpoint for disabilitas type detail, update, and delete"""
    try:
        disability_type = get_object_or_404(DisabilitasType, pk=pk)
        
        if request.method == 'GET':
            data = {
                'id': disability_type.id,
                'name': disability_type.name,
                'code': disability_type.code,
                'description': disability_type.description,
                'is_active': disability_type.is_active
            }
            return JsonResponse(data)
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            form = DisabilitasTypeForm(data, instance=disability_type)
            
            if form.is_valid():
                disability_type = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Jenis disabilitas berhasil diperbarui'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        
        elif request.method == 'DELETE':
            # Check if disability type has data
            if DisabilitasData.objects.filter(disability_type=disability_type).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Tidak dapat menghapus jenis disabilitas yang masih memiliki data'
                }, status=400)
            
            disability_type.delete()
            return JsonResponse({
                'success': True,
                'message': 'Jenis disabilitas berhasil dihapus'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Disabilitas Data Views
@csrf_exempt
def disabilitas_data_list_api(request):
    """API endpoint for disabilitas data list with pagination and search"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        
        queryset = DisabilitasData.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(penduduk__name__icontains=search) |
                Q(penduduk__nik__icontains=search) |
                Q(disability_type__name__icontains=search)
            )
        
        queryset = queryset.select_related('penduduk', 'disability_type').order_by('-created_at')
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': dd.id,
                    'penduduk_name': dd.penduduk.name,
                    'penduduk_nik': dd.penduduk.nik,
                    'disability_type': dd.disability_type.name,
                    'severity': dd.get_severity_display(),
                    'needs_assistance': dd.needs_assistance,
                    'diagnosis_date': dd.diagnosis_date.strftime('%d/%m/%Y') if dd.diagnosis_date else '',
                    'is_active': dd.is_active,
                    'created_at': dd.created_at.strftime('%d/%m/%Y %H:%M')
                } for dd in page_obj
            ],
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def disabilitas_data_create_api(request):
    """API endpoint for creating disabilitas data"""
    if request.method == 'GET':
        # Return form data for modal
        penduduk_list = [{'id': p.id, 'name': p.name, 'nik': p.nik} for p in Penduduk.objects.all()]
        disability_types = [{'id': dt.id, 'name': dt.name} for dt in DisabilitasType.objects.filter(is_active=True)]
        
        return JsonResponse({
            'penduduk_choices': penduduk_list,
            'disability_type_choices': disability_types,
            'severity_choices': [{'value': k, 'label': v} for k, v in DisabilitasData.SEVERITY_CHOICES]
        })
    
    try:
        data = json.loads(request.body)
        form = DisabilitasDataForm(data)
        
        if form.is_valid():
            disability_data = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data disabilitas berhasil ditambahkan',
                'data': {
                    'id': disability_data.id,
                    'penduduk_name': disability_data.penduduk.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "PUT", "DELETE"])
def disabilitas_data_detail_api(request, pk):
    """API endpoint for disabilitas data detail, update, and delete"""
    try:
        disability_data = get_object_or_404(DisabilitasData, pk=pk)
        
        if request.method == 'GET':
            data = {
                'id': disability_data.id,
                'penduduk_id': disability_data.penduduk.id,
                'disability_type_id': disability_data.disability_type.id,
                'severity': disability_data.severity,
                'description': disability_data.description,
                'diagnosis_date': disability_data.diagnosis_date.strftime('%Y-%m-%d') if disability_data.diagnosis_date else '',
                'needs_assistance': disability_data.needs_assistance,
                'is_active': disability_data.is_active
            }
            return JsonResponse(data)
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            form = DisabilitasDataForm(data, instance=disability_data)
            
            if form.is_valid():
                disability_data = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Data disabilitas berhasil diperbarui'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        
        elif request.method == 'DELETE':
            disability_data.delete()
            return JsonResponse({
                'success': True,
                'message': 'Data disabilitas berhasil dihapus'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Individual Admin Pages
# Duplicate admin views removed - keeping only the first definitions

@login_required
@user_passes_test(is_admin)
def add_penduduk(request):
    """Add new penduduk page"""
    context = {
        'page_title': 'Tambah Data Penduduk',
        'page_subtitle': 'Isi formulir untuk menambahkan data penduduk baru'
    }
    return render(request, 'admin/modules/references/add_penduduk.html', context)

@login_required
@user_passes_test(is_admin)
def add_penduduk_new(request):
    """New add penduduk page with enhanced form"""
    context = {
        'page_title': 'Tambah Data Penduduk',
        'page_subtitle': 'Form lengkap untuk menambahkan data penduduk baru'
    }
    return render(request, 'admin/modules/references/addpenduduk.html', context)

@login_required
@user_passes_test(is_admin)
def edit_penduduk(request, pk):
    """Edit penduduk page"""
    context = {
        'page_title': 'Edit Data Penduduk',
        'page_subtitle': 'Ubah data penduduk',
        'penduduk_id': pk
    }
    return render(request, 'admin/modules/references/editpenduduk.html', context)

@login_required
@user_passes_test(is_admin)
def add_dusun(request):
    """Add new dusun page"""
    context = {
        'page_title': 'Tambah Data Dusun',
        'page_subtitle': 'Isi formulir untuk menambahkan data dusun baru'
    }
    return render(request, 'admin/modules/references/add_dusun.html', context)

@login_required
@user_passes_test(is_admin)
def edit_dusun(request, pk):
    """Edit dusun page"""
    context = {
        'page_title': 'Edit Data Dusun',
        'page_subtitle': 'Ubah data dusun',
        'dusun_id': pk
    }
    return render(request, 'admin/modules/references/edit_dusun.html', context)

@login_required
@user_passes_test(is_admin)
def disabilitas_admin(request):
    """Admin page for Disabilitas management"""
    context = {
        'page_title': 'Input Data Disabilitas',
        'page_subtitle': 'Kelola data penyandang disabilitas'
    }
    return render(request, 'admin/modules/references/disabilitas.html', context)


@login_required
@user_passes_test(is_admin)
def family_admin(request):
    """Admin page for Family management"""
    context = {
        'page_title': 'Input Data Keluarga',
        'page_subtitle': 'Kelola data keluarga'
    }
    return render(request, 'admin/modules/references/family.html', context)



@login_required
@user_passes_test(is_admin)
def dashboard_summary_api(request):
    """Enhanced API endpoint for dashboard summary with more detailed statistics"""
    try:
        # Calculate comprehensive statistics
        stats = {
            # Basic counts
            'total_dusun': Dusun.objects.filter(is_active=True).count(),
            'total_lorong': Lorong.objects.filter(is_active=True).count(),
            'total_penduduk': Penduduk.objects.filter(is_active=True).count(),
            'total_disabilitas': DisabilitasData.objects.filter(is_active=True).count(),
            
            # Demographics
            'male_percentage': 0,
            'female_percentage': 0,
            'average_age': 0,
            
            # Recent growth (last 30 days)
            'new_residents_month': 0,
            'new_disabilities_month': 0,
            
            # Disability insights
            'disability_percentage': 0,
            'needs_assistance_count': 0,
            
            # Geographic distribution
            'avg_population_per_dusun': 0,
            'avg_houses_per_lorong': 0,
        }
        
        total_penduduk = Penduduk.objects.filter(is_active=True).count()
        
        if total_penduduk > 0:
            # Demographics calculations
            male_count = Penduduk.objects.filter(jenis_kelamin='L', is_active=True).count()
            female_count = Penduduk.objects.filter(jenis_kelamin='P', is_active=True).count()
            
            stats['male_percentage'] = round((male_count / total_penduduk) * 100, 1)
            stats['female_percentage'] = round((female_count / total_penduduk) * 100, 1)
            
            # Average age calculation
            today = date.today()
            ages = []
            for p in Penduduk.objects.filter(is_active=True):
                if p.tanggal_lahir:
                    age = today.year - p.tanggal_lahir.year - ((today.month, today.day) < (p.tanggal_lahir.month, p.tanggal_lahir.day))
                    ages.append(age)
            stats['average_age'] = round(sum(ages) / len(ages), 1) if ages else 0
            
            # Disability statistics
            total_disabilitas = DisabilitasData.objects.filter(is_active=True).count()
            stats['disability_percentage'] = round((total_disabilitas / total_penduduk) * 100, 1)
            stats['needs_assistance_count'] = DisabilitasData.objects.filter(
                is_active=True, 
                needs_assistance=True
            ).count()
        
        # Recent activity (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        stats['new_residents_month'] = Penduduk.objects.filter(
            created_at__gte=thirty_days_ago,
            is_active=True
        ).count()
        
        stats['new_disabilities_month'] = DisabilitasData.objects.filter(
            created_at__gte=thirty_days_ago,
            is_active=True
        ).count()
        
        # Geographic averages
        active_dusun_count = Dusun.objects.filter(is_active=True).count()
        if active_dusun_count > 0:
            stats['avg_population_per_dusun'] = round(total_penduduk / active_dusun_count, 0)
        
        active_lorong_count = Lorong.objects.filter(is_active=True).count()
        if active_lorong_count > 0:
            total_houses = Lorong.objects.filter(is_active=True).aggregate(
                total=Sum('house_count')
            )['total'] or 0
            stats['avg_houses_per_lorong'] = round(total_houses / active_lorong_count, 1)
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Family Views
@csrf_exempt
def family_list_api(request):
    """API endpoint for family list with pagination and search"""
    try:
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '').strip()
        
        families = Family.objects.filter(is_active=True)
        
        if search:
            families = families.filter(
                Q(kk_number__icontains=search) |
                Q(head__name__icontains=search) |
                Q(head__nik__icontains=search) |
                Q(address__icontains=search)
            )
        
        # Calculate total before pagination
        total_count = families.count()
        
        # Apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        families = families[start:end]
        
        # Serialize data
        family_data = []
        for family in families:
            family_data.append({
                'id': family.id,
                'kk_number': family.kk_number,
                'head_name': family.head.name,
                'head_nik': family.head.nik,
                'family_status': family.family_status,
                'total_members': family.total_members,
                'total_income': float(family.total_income) if family.total_income else None,
                'dusun': family.dusun.name,
                'lorong': family.lorong.name if family.lorong else None,
                'address': family.address,
                'phone_number': family.phone_number,
                'is_active': family.is_active,
                'created_at': family.created_at.strftime('%Y-%m-%d %H:%M:%S') if family.created_at else None,
            })
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_previous = page > 1
        has_next = page < total_pages
        
        response_data = {
            'results': family_data,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_items': total_count,
                'total_pages': total_pages,
                'has_previous': has_previous,
                'has_next': has_next,
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def family_create_api(request):
    """API endpoint for creating family"""
    if request.method == 'GET':
        # Return form data for modal
        dusun_list = [{'id': d.id, 'name': d.name} for d in Dusun.objects.all()]
        lorong_list = [{'id': l.id, 'name': l.name} for l in Lorong.objects.all()]
        head_choices = [{'id': p.id, 'name': f"{p.name} ({p.nik})"} for p in Penduduk.objects.filter(is_active=True).order_by('name')]
        
        return JsonResponse({
            'dusun_choices': dusun_list,
            'lorong_choices': lorong_list,
            'head_choices': head_choices,
            'family_status_choices': [{'value': k, 'label': v} for k, v in Family.FAMILY_STATUS_CHOICES],
        })
    
    try:
        data = json.loads(request.body)
        form = FamilyForm(data)
        
        if form.is_valid():
            family = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Data keluarga berhasil ditambahkan',
                'data': {
                    'id': family.id,
                    'kk_number': family.kk_number,
                    'head_name': family.head.name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "PUT", "DELETE"])
def family_detail_api(request, pk):
    """API endpoint for family detail, update, and delete"""
    try:
        family = get_object_or_404(Family, pk=pk)
        
        if request.method == 'GET':
            data = {
                'id': family.id,
                'kk_number': family.kk_number,
                'head_id': family.head.id if family.head else None,
                'family_status': family.family_status,
                'total_members': family.total_members,
                'total_income': float(family.total_income) if family.total_income else None,
                'address': family.address,
                'dusun_id': family.dusun.id if family.dusun else None,
                'lorong_id': family.lorong.id if family.lorong else None,
                'rt_number': family.rt_number,
                'rw_number': family.rw_number,
                'house_number': family.house_number,
                'postal_code': family.postal_code,
                'phone_number': family.phone_number,
                'is_active': family.is_active,
            }
            return JsonResponse(data)
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            form = FamilyForm(data, instance=family)
            
            if form.is_valid():
                family = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Data keluarga berhasil diperbarui'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
        
        elif request.method == 'DELETE':
            family.delete()
            return JsonResponse({
                'success': True,
                'message': 'Data keluarga berhasil dihapus'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
