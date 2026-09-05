from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, date
import json

from .models import (
    PosyanduLocation, PosyanduSchedule, HealthRecord, 
    Immunization, NutritionData, PosyanduKader, IbuHamil, 
    PemeriksaanIbuHamil, StuntingData
)
from references.models import Penduduk, Dusun, Lorong


@login_required
def posyandu_module(request):
    """Main posyandu module view"""
    context = {
        'page_title': 'Manajemen Posyandu',
        'page_subtitle': 'Kelola data posyandu, jadwal, dan kesehatan'
    }
    return render(request, 'admin/modules/posyandu.html', context)


# ============= POSYANDU LOCATION VIEWS =============

@login_required
def posyandu_location_list(request):
    """List posyandu locations with pagination and search"""
    search = request.GET.get('search', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    locations = PosyanduLocation.objects.all()
    
    if search:
        locations = locations.filter(
            Q(name__icontains=search) |
            Q(address__icontains=search) |
            Q(coordinator__name__icontains=search)
        )
    
    locations = locations.select_related('coordinator').order_by('-created_at')
    
    paginator = Paginator(locations, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for location in page_obj:
        data.append({
            'id': location.id,
            'name': location.name,
            'address': location.address,
            'coordinator': location.coordinator.name if location.coordinator else '-',
            'contact_phone': location.contact_phone,
            'capacity': location.capacity,
            'facilities': location.facilities,
            'is_active': location.is_active,
            'established_date': location.established_date.strftime('%Y-%m-%d') if location.established_date else '-',
            'created_at': location.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
        }
    })


@login_required
def posyandu_location_detail(request, location_id):
    """Get posyandu location detail"""
    location = get_object_or_404(PosyanduLocation, id=location_id)
    
    data = {
        'id': location.id,
        'name': location.name,
        'address': location.address,
        'coordinator_id': location.coordinator.id if location.coordinator else None,
        'coordinator_name': location.coordinator.name if location.coordinator else '-',
        'contact_phone': location.contact_phone,
        'capacity': location.capacity,
        'facilities': location.facilities,
        'is_active': location.is_active,
        'established_date': location.established_date.strftime('%Y-%m-%d') if location.established_date else '',
        'created_at': location.created_at.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse({'data': data})


@login_required
@require_http_methods(["POST"])
def posyandu_location_create(request):
    """Create new posyandu location"""
    try:
        data = json.loads(request.body)
        
        coordinator = None
        if data.get('coordinator_id'):
            coordinator = get_object_or_404(Penduduk, id=data['coordinator_id'])
        
        established_date = None
        if data.get('established_date'):
            established_date = datetime.strptime(data['established_date'], '%Y-%m-%d').date()
        
        location = PosyanduLocation.objects.create(
            name=data['name'],
            address=data['address'],
            coordinator=coordinator,
            contact_phone=data.get('contact_phone', ''),
            capacity=data.get('capacity', 50),
            facilities=data.get('facilities', ''),
            is_active=data.get('is_active', True),
            established_date=established_date
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Lokasi posyandu berhasil ditambahkan',
            'data': {
                'id': location.id,
                'name': location.name
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan lokasi posyandu: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["PUT"])
def posyandu_location_update(request, location_id):
    """Update posyandu location"""
    try:
        location = get_object_or_404(PosyanduLocation, id=location_id)
        data = json.loads(request.body)
        
        coordinator = None
        if data.get('coordinator_id'):
            coordinator = get_object_or_404(Penduduk, id=data['coordinator_id'])
        
        established_date = None
        if data.get('established_date'):
            established_date = datetime.strptime(data['established_date'], '%Y-%m-%d').date()
        
        location.name = data['name']
        location.address = data['address']
        location.coordinator = coordinator
        location.contact_phone = data.get('contact_phone', '')
        location.capacity = data.get('capacity', 50)
        location.facilities = data.get('facilities', '')
        location.is_active = data.get('is_active', True)
        location.established_date = established_date
        location.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Lokasi posyandu berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui lokasi posyandu: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE"])
def posyandu_location_delete(request, location_id):
    """Delete posyandu location"""
    try:
        location = get_object_or_404(PosyanduLocation, id=location_id)
        location_name = location.name
        location.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Lokasi posyandu "{location_name}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus lokasi posyandu: {str(e)}'
        }, status=400)


# ============= POSYANDU SCHEDULE VIEWS =============

@login_required
def posyandu_schedule_list(request):
    """List posyandu schedules with pagination and search"""
    search = request.GET.get('search', '')
    location_id = request.GET.get('location_id', '')
    activity_type = request.GET.get('activity_type', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    schedules = PosyanduSchedule.objects.all()
    
    if search:
        schedules = schedules.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(location__name__icontains=search)
        )
    
    if location_id:
        schedules = schedules.filter(location_id=location_id)
    
    if activity_type:
        schedules = schedules.filter(activity_type=activity_type)
    
    schedules = schedules.select_related('location', 'created_by').order_by('-schedule_date', 'start_time')
    
    paginator = Paginator(schedules, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for schedule in page_obj:
        data.append({
            'id': schedule.id,
            'title': schedule.title,
            'description': schedule.description,
            'location_name': schedule.location.name,
            'activity_type': schedule.get_activity_type_display(),
            'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d'),
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'target_participants': schedule.target_participants,
            'actual_participants': schedule.actual_participants,
            'is_completed': schedule.is_completed,
            'created_by': schedule.created_by.username if schedule.created_by else '-',
            'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })


@login_required
def posyandu_schedule_detail(request, schedule_id):
    """Get posyandu schedule detail"""
    schedule = get_object_or_404(PosyanduSchedule, id=schedule_id)
    
    data = {
        'id': schedule.id,
        'location_id': schedule.location.id,
        'location_name': schedule.location.name,
        'activity_type': schedule.activity_type,
        'title': schedule.title,
        'description': schedule.description,
        'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d'),
        'start_time': schedule.start_time.strftime('%H:%M'),
        'end_time': schedule.end_time.strftime('%H:%M'),
        'target_participants': schedule.target_participants,
        'actual_participants': schedule.actual_participants,
        'notes': schedule.notes,
        'is_completed': schedule.is_completed,
        'created_by': schedule.created_by.username if schedule.created_by else '-',
        'created_at': schedule.created_at.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse({'data': data})


@login_required
@require_http_methods(["POST"])
def posyandu_schedule_create(request):
    """Create new posyandu schedule"""
    try:
        data = json.loads(request.body)
        
        location = get_object_or_404(PosyanduLocation, id=data['location_id'])
        schedule_date = datetime.strptime(data['schedule_date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        schedule = PosyanduSchedule.objects.create(
            location=location,
            activity_type=data['activity_type'],
            title=data['title'],
            description=data.get('description', ''),
            schedule_date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            target_participants=data.get('target_participants', 0),
            actual_participants=data.get('actual_participants', 0),
            notes=data.get('notes', ''),
            is_completed=data.get('is_completed', False),
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Jadwal posyandu berhasil ditambahkan',
            'data': {
                'id': schedule.id,
                'title': schedule.title
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan jadwal posyandu: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["PUT"])
def posyandu_schedule_update(request, schedule_id):
    """Update posyandu schedule"""
    try:
        schedule = get_object_or_404(PosyanduSchedule, id=schedule_id)
        data = json.loads(request.body)
        
        location = get_object_or_404(PosyanduLocation, id=data['location_id'])
        schedule_date = datetime.strptime(data['schedule_date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        schedule.location = location
        schedule.activity_type = data['activity_type']
        schedule.title = data['title']
        schedule.description = data.get('description', '')
        schedule.schedule_date = schedule_date
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.target_participants = data.get('target_participants', 0)
        schedule.actual_participants = data.get('actual_participants', 0)
        schedule.notes = data.get('notes', '')
        schedule.is_completed = data.get('is_completed', False)
        schedule.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Jadwal posyandu berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui jadwal posyandu: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE"])
def posyandu_schedule_delete(request, schedule_id):
    """Delete posyandu schedule"""
    try:
        schedule = get_object_or_404(PosyanduSchedule, id=schedule_id)
        schedule_title = schedule.title
        schedule.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Jadwal "{schedule_title}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus jadwal: {str(e)}'
        }, status=400)


# ============= HEALTH RECORD VIEWS =============

@login_required
def health_record_list(request):
    """List health records with pagination and search"""
    search = request.GET.get('search', '')
    patient_type = request.GET.get('patient_type', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    records = HealthRecord.objects.all()
    
    if search:
        records = records.filter(
            Q(patient__name__icontains=search) |
            Q(patient__nik__icontains=search) |
            Q(diagnosis__icontains=search) |
            Q(complaints__icontains=search)
        )
    
    if patient_type:
        records = records.filter(patient_type=patient_type)
    
    if posyandu_id:
        records = records.filter(posyandu_id=posyandu_id)
    
    records = records.select_related('patient', 'posyandu', 'recorded_by').order_by('-visit_date')
    
    paginator = Paginator(records, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for record in page_obj:
        data.append({
            'id': record.id,
            'patient_name': record.patient.name,
            'patient_nik': record.patient.nik,
            'posyandu_name': record.posyandu.name,
            'patient_type': record.get_patient_type_display(),
            'visit_date': record.visit_date.strftime('%Y-%m-%d'),
            'weight': float(record.weight) if record.weight else None,
            'height': float(record.height) if record.height else None,
            'blood_pressure': record.blood_pressure,
            'temperature': float(record.temperature) if record.temperature else None,
            'complaints': record.complaints,
            'diagnosis': record.diagnosis,
            'treatment': record.treatment,
            'next_visit': record.next_visit.strftime('%Y-%m-%d') if record.next_visit else None,
            'recorded_by': record.recorded_by.username if record.recorded_by else '-',
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })


# ============= IMMUNIZATION VIEWS =============

@login_required
def immunization_list(request):
    """List immunizations with pagination and search"""
    search = request.GET.get('search', '')
    vaccine_type = request.GET.get('vaccine_type', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    immunizations = Immunization.objects.all()
    
    if search:
        immunizations = immunizations.filter(
            Q(patient__name__icontains=search) |
            Q(patient__nik__icontains=search) |
            Q(vaccine_name__icontains=search)
        )
    
    if vaccine_type:
        immunizations = immunizations.filter(vaccine_type=vaccine_type)
    
    if posyandu_id:
        immunizations = immunizations.filter(posyandu_id=posyandu_id)
    
    immunizations = immunizations.select_related('patient', 'posyandu', 'administered_by').order_by('-immunization_date')
    
    paginator = Paginator(immunizations, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for immunization in page_obj:
        data.append({
            'id': immunization.id,
            'patient_name': immunization.patient.name,
            'patient_nik': immunization.patient.nik,
            'posyandu_name': immunization.posyandu.name,
            'vaccine_type': immunization.get_vaccine_type_display(),
            'vaccine_name': immunization.vaccine_name,
            'dose_number': immunization.dose_number,
            'immunization_date': immunization.immunization_date.strftime('%Y-%m-%d'),
            'batch_number': immunization.batch_number,
            'expiry_date': immunization.expiry_date.strftime('%Y-%m-%d') if immunization.expiry_date else None,
            'side_effects': immunization.side_effects,
            'next_dose_date': immunization.next_dose_date.strftime('%Y-%m-%d') if immunization.next_dose_date else None,
            'administered_by': immunization.administered_by.username if immunization.administered_by else '-',
            'created_at': immunization.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })


# ============= NUTRITION DATA VIEWS =============

@login_required
def nutrition_data_list(request):
    """List nutrition data with pagination and search"""
    search = request.GET.get('search', '')
    nutrition_status = request.GET.get('nutrition_status', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    nutrition_data = NutritionData.objects.all()
    
    if search:
        nutrition_data = nutrition_data.filter(
            Q(patient__name__icontains=search) |
            Q(patient__nik__icontains=search)
        )
    
    if nutrition_status:
        nutrition_data = nutrition_data.filter(nutrition_status=nutrition_status)
    
    if posyandu_id:
        nutrition_data = nutrition_data.filter(posyandu_id=posyandu_id)
    
    nutrition_data = nutrition_data.select_related('patient', 'posyandu', 'recorded_by').order_by('-measurement_date')
    
    paginator = Paginator(nutrition_data, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for nutrition in page_obj:
        data.append({
            'id': nutrition.id,
            'patient_name': nutrition.patient.name,
            'patient_nik': nutrition.patient.nik,
            'posyandu_name': nutrition.posyandu.name,
            'measurement_date': nutrition.measurement_date.strftime('%Y-%m-%d'),
            'age_months': nutrition.age_months,
            'weight': float(nutrition.weight),
            'height': float(nutrition.height),
            'head_circumference': float(nutrition.head_circumference) if nutrition.head_circumference else None,
            'arm_circumference': float(nutrition.arm_circumference) if nutrition.arm_circumference else None,
            'nutrition_status': nutrition.get_nutrition_status_display(),
            'vitamin_a_given': nutrition.vitamin_a_given,
            'iron_supplement_given': nutrition.iron_supplement_given,
            'notes': nutrition.notes,
            'recorded_by': nutrition.recorded_by.username if nutrition.recorded_by else '-',
            'created_at': nutrition.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })


# ============= STATISTICS API =============

@login_required
def posyandu_stats(request):
    """Get posyandu statistics"""
    try:
        # Basic counts
        total_locations = PosyanduLocation.objects.filter(is_active=True).count()
        total_schedules = PosyanduSchedule.objects.count()
        total_health_records = HealthRecord.objects.count()
        total_immunizations = Immunization.objects.count()
        
        # New specific counts for dashboard
        total_kader = PosyanduKader.objects.filter(status='aktif').count()
        total_ibu_hamil = IbuHamil.objects.filter(status_aktif=True).count()
        total_stunting = StuntingData.objects.count()
        
        # Count balita (children under 5 years old)
        today = date.today()
        balita = Penduduk.objects.filter(
            birth_date__gte=today.replace(year=today.year-5)
        ).count()
        
        # Count lansia (elderly 60+ years old)
        lansia = Penduduk.objects.filter(
            birth_date__lte=today.replace(year=today.year-60)
        ).count()
        
        # Recent activities
        recent_schedules = PosyanduSchedule.objects.filter(
            schedule_date__gte=date.today()
        ).count()
        
        # Patient type distribution
        patient_types = HealthRecord.objects.values('patient_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Nutrition status distribution
        nutrition_status = NutritionData.objects.values('nutrition_status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Vaccine type distribution
        vaccine_types = Immunization.objects.values('vaccine_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Stunting status distribution
        stunting_status = StuntingData.objects.values('status_stunting').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Pregnancy risk distribution
        pregnancy_risk = IbuHamil.objects.values('risiko_kehamilan').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Calculate growth percentages and additional stats for dashboard
        balita_growth = 0  # You can implement actual growth calculation
        ibu_hamil_growth = 0  # You can implement actual growth calculation
        stunting_percentage = round((total_stunting / max(balita, 1)) * 100, 1) if balita > 0 else 0
        
        return JsonResponse({
            'success': True,
            'stats': {
                'total_balita': balita,
                'total_ibu_hamil': total_ibu_hamil,
                'total_kader': total_kader,
                'total_stunting': total_stunting,
                'balita_growth': balita_growth,
                'ibu_hamil_growth': ibu_hamil_growth,
                'stunting_percentage': stunting_percentage
            },
            'health_status': {
                'normal': 0,  # Calculate from actual data
                'warning': 0,  # Calculate from actual data
                'critical': 0,  # Calculate from actual data
                'nutrition': {
                    'gizi_normal': 0,
                    'gizi_kurang': 0,
                    'gizi_buruk': 0,
                    'stunting': total_stunting
                }
            },
            'monthly_activity': {
                'balita_checkups': 0,  # Calculate from actual data
                'ibu_hamil_checkups': 0,  # Calculate from actual data
                'immunizations': 0,  # Calculate from actual data
                'vitamin_a': 0  # Calculate from actual data
            },
            'recent_activity': {
                'balita_records': 0,  # Calculate from actual data
                'ibu_hamil_records': 0,  # Calculate from actual data
                'immunizations': 0,  # Calculate from actual data
                'growth_monitoring': 0  # Calculate from actual data
            },
            'raw_data': {
                'total_locations': total_locations,
                'total_schedules': total_schedules,
                'total_health_records': total_health_records,
                'total_immunizations': total_immunizations,
                'recent_schedules': recent_schedules,
                'patient_types': list(patient_types),
                'nutrition_status': list(nutrition_status),
                'vaccine_types': list(vaccine_types),
                'stunting_status': list(stunting_status),
                'pregnancy_risk': list(pregnancy_risk)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Gagal memuat statistik posyandu: {str(e)}'
        }, status=500)


# ============= SPECIFIC STATISTICS API =============

@require_http_methods(["GET"])
def balita_stats_api(request):
    """Get balita statistics"""
    try:
        today = date.today()
        total_balita = Penduduk.objects.filter(
            birth_date__gte=today.replace(year=today.year-5)
        ).count()
        
        # Get nutrition status counts
        normal = NutritionData.objects.filter(
            patient__birth_date__gte=today.replace(year=today.year-5),
            nutrition_status='normal'
        ).count()
        
        kurang = NutritionData.objects.filter(
            patient__birth_date__gte=today.replace(year=today.year-5),
            nutrition_status='kurang'
        ).count()
        
        stunting = StuntingData.objects.filter(
            status_stunting__in=['pendek', 'sangat_pendek']
        ).count()
        
        return JsonResponse({
            'total': total_balita,
            'normal': normal,
            'kurang': kurang,
            'stunting': stunting
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Gagal memuat statistik balita: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def kader_stats_api(request):
    """Get kader statistics"""
    try:
        total = PosyanduKader.objects.count()
        active = PosyanduKader.objects.filter(status='aktif').count()
        leader = PosyanduKader.objects.filter(jabatan='ketua', status='aktif').count()
        inactive = PosyanduKader.objects.filter(status='nonaktif').count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'total': total,
                'aktif': active,
                'ketua': leader,
                'nonaktif': inactive
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memuat statistik kader: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def ibu_hamil_stats_api(request):
    """Get ibu hamil statistics"""
    try:
        total = IbuHamil.objects.filter(status_aktif=True).count()
        trimester1 = IbuHamil.objects.filter(status_aktif=True, usia_kehamilan__lte=12).count()
        trimester2 = IbuHamil.objects.filter(status_aktif=True, usia_kehamilan__gt=12, usia_kehamilan__lte=28).count()
        trimester3 = IbuHamil.objects.filter(status_aktif=True, usia_kehamilan__gt=28).count()
        
        return JsonResponse({
            'total': total,
            'trimester1': trimester1,
            'trimester2': trimester2,
            'trimester3': trimester3
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Gagal memuat statistik ibu hamil: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def stunting_stats_api(request):
    """Get stunting statistics"""
    try:
        total = StuntingData.objects.count()
        severe = StuntingData.objects.filter(status_stunting='stunting_berat').count()
        moderate = StuntingData.objects.filter(status_stunting='stunting_sedang').count()
        interventions = StuntingData.objects.exclude(intervensi_diberikan='').count()
        
        return JsonResponse({
            'total': total,
            'severe': severe,
            'moderate': moderate,
            'interventions': interventions
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Gagal memuat statistik stunting: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def lansia_stats_api(request):
    """Get lansia statistics"""
    try:
        today = date.today()
        
        # Get lansia from penduduk based on age (60+ years)
        lansia = Penduduk.objects.filter(
            birth_date__lte=today.replace(year=today.year-60)
        )
        
        total_lansia = lansia.count()
        healthy = 0
        attention = 0
        sick = 0
        
        # Count health status based on latest health records
        for l in lansia:
            latest_record = HealthRecord.objects.filter(
                patient=l, 
                patient_type='lansia'
            ).order_by('-visit_date').first()
            
            if latest_record:
                if latest_record.diagnosis and latest_record.diagnosis.strip():
                    if 'sehat' in latest_record.diagnosis.lower():
                        healthy += 1
                    elif 'perhatian' in latest_record.diagnosis.lower():
                        attention += 1
                    else:
                        sick += 1
                else:
                    # No diagnosis means healthy
                    healthy += 1
            else:
                # No health record means healthy
                healthy += 1
        
        return JsonResponse({
            'total': total_lansia,
            'healthy': healthy,
            'attention': attention,
            'sick': sick
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Gagal memuat statistik lansia: {str(e)}'
        }, status=500)


# ============= HELPER VIEWS =============

@login_required
def get_posyandu_locations(request):
    """Get all active posyandu locations for dropdown"""
    locations = PosyanduLocation.objects.filter(is_active=True).values('id', 'name')
    return JsonResponse({'results': list(locations)})


@login_required
def get_residents_for_posyandu(request):
    """Get residents for posyandu selection"""
    search = request.GET.get('search', '')
    age_max = request.GET.get('age_max', '')
    age_min = request.GET.get('age_min', '')
    gender = request.GET.get('gender', '')
    residents = Penduduk.objects.all()
    
    if search:
        residents = residents.filter(
            Q(name__icontains=search) |
            Q(nik__icontains=search)
        )
    
    # Filter by gender if provided
    if gender:
        residents = residents.filter(gender=gender)
    
    residents = residents.values('id', 'name', 'nik', 'birth_date', 'gender')[:50]
    
    data = []
    for resident in residents:
        age = None
        if resident['birth_date']:
            today = date.today()
            age = today.year - resident['birth_date'].year
            if today.month < resident['birth_date'].month or \
               (today.month == resident['birth_date'].month and today.day < resident['birth_date'].day):
                age -= 1
        
        # Filter by age_max if provided
        if age_max and age is not None:
            try:
                max_age = int(age_max)
                if age > max_age:
                    continue
            except ValueError:
                pass
        
        # Filter by age_min if provided
        if age_min and age is not None:
            try:
                min_age = int(age_min)
                if age < min_age:
                    continue
            except ValueError:
                pass
        
        data.append({
            'id': resident['id'],
            'name': resident['name'],
            'nik': resident['nik'],
            'age': age,
            'gender': resident['gender']
        })
    
    return JsonResponse({'results': data})


@login_required
def get_ibu_hamil_dropdown(request):
    """Get ibu hamil for dropdown selection"""
    search = request.GET.get('search', '')
    ibu_hamil = IbuHamil.objects.filter(status_aktif=True)
    
    if search:
        ibu_hamil = ibu_hamil.filter(
            Q(penduduk__name__icontains=search) |
            Q(penduduk__nik__icontains=search)
        )
    
    ibu_hamil = ibu_hamil.select_related('penduduk', 'posyandu')[:20]
    
    data = []
    for ibu in ibu_hamil:
        data.append({
            'id': ibu.id,
            'name': ibu.penduduk.name,
            'nik': ibu.penduduk.nik,
            'posyandu': ibu.posyandu.name,
            'usia_kehamilan': ibu.usia_kehamilan
        })
    
    return JsonResponse({'results': data})


@require_http_methods(["GET"])
def get_children_for_posyandu(request):
    """Get children (balita) for dropdown selection - age 1-3 years"""
    search = request.GET.get('search', '')
    
    # Filter children aged 1-3 years from Penduduk
    from datetime import timedelta
    today = date.today()
    three_years_ago = today - timedelta(days=3*365)
    one_year_ago = today - timedelta(days=1*365)
    
    children = Penduduk.objects.filter(
        birth_date__gte=three_years_ago,
        birth_date__lte=one_year_ago,
        birth_date__isnull=False
    )
    
    if search:
        children = children.filter(
            Q(name__icontains=search) |
            Q(nik__icontains=search)
        )
    
    children = children.order_by('name')[:20]
    
    data = []
    for child in children:
        # Calculate age from birth date
        age_months = 0
        if child.birth_date:
            birth_date = child.birth_date
            age_months = (today.year - birth_date.year) * 12 + today.month - birth_date.month
        
        data.append({
            'id': child.id,
            'name': child.name,
            'nik': child.nik,
            'age_months': age_months,
            'birth_date': child.birth_date.strftime('%Y-%m-%d') if child.birth_date else None
        })
    
    return JsonResponse({'results': data})


@login_required
def posyandu_dashboard(request):
    """Main posyandu dashboard"""
    from datetime import timedelta
    
    # Basic statistics
    total_balita = Penduduk.objects.filter(
        birth_date__gte=date.today().replace(year=date.today().year-5)
    ).count()
    
    total_ibu_hamil = IbuHamil.objects.filter(status_aktif=True).count()
    total_kader = PosyanduKader.objects.filter(status='aktif').count()
    total_stunting = StuntingData.objects.count()
    
    # Calculate growth (mock data for now)
    balita_growth = 5
    ibu_hamil_growth = 3
    
    # Calculate stunting percentage
    stunting_percentage = round((total_stunting / total_balita * 100) if total_balita > 0 else 0, 1)
    
    stats = {
        'total_balita': total_balita,
        'total_ibu_hamil': total_ibu_hamil,
        'total_kader': total_kader,
        'total_stunting': total_stunting,
        'balita_growth': balita_growth,
        'ibu_hamil_growth': ibu_hamil_growth,
        'stunting_percentage': stunting_percentage,
    }
    
    # Health status overview (mock percentages)
    health_status = {
        'normal_percentage': 75,
        'warning_percentage': 20,
        'critical_percentage': 5,
    }
    
    # Nutrition data (mock data)
    nutrition = {
        'gizi_normal': int(total_balita * 0.7),
        'gizi_kurang': int(total_balita * 0.2),
        'gizi_buruk': int(total_balita * 0.05),
        'stunting': total_stunting,
        'gizi_normal_percentage': 70,
        'gizi_kurang_percentage': 20,
        'gizi_buruk_percentage': 5,
        'stunting_percentage': stunting_percentage,
    }
    
    # Posyandu locations
    posyandu_locations = PosyanduLocation.objects.filter(is_active=True)[:5]
    
    # Monthly activity (mock data)
    monthly_activity = {
        'balita_checkups': 45,
        'ibu_hamil_checkups': 23,
        'immunizations': 38,
        'vitamin_a': 42,
    }
    
    # Recent activity (last 7 days - mock data)
    recent_activity = {
        'balita_records': 8,
        'ibu_hamil_records': 5,
        'immunizations': 12,
        'growth_monitoring': 15,
    }
    
    # Upcoming schedules
    upcoming_schedules = PosyanduSchedule.objects.filter(
        schedule_date__gte=date.today()
    ).select_related('location').order_by('schedule_date')[:5]
    
    context = {
        'page_title': 'Dashboard Posyandu',
        'page_subtitle': 'Overview data posyandu dan kesehatan',
        'stats': stats,
        'health_status': health_status,
        'nutrition': nutrition,
        'posyandu_locations': posyandu_locations,
        'monthly_activity': monthly_activity,
        'recent_activity': recent_activity,
        'upcoming_schedules': upcoming_schedules,
    }
    return render(request, 'admin/modules/posyandu/index.html', context)

@login_required
def kader_admin(request):
    """Kader admin page"""
    # Get filter parameters
    search = request.GET.get('search', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')
    page = request.GET.get('page', 1)
    per_page = 10
    
    # Get kader data
    kader_list = PosyanduKader.objects.all()
    
    # Apply filters
    if search:
        kader_list = kader_list.filter(
            Q(penduduk__name__icontains=search) |
            Q(penduduk__nik__icontains=search)
        )
    
    if posyandu_id:
        kader_list = kader_list.filter(posyandu_id=posyandu_id)
    
    if role:
        kader_list = kader_list.filter(jabatan=role)
    
    if status:
        # Map frontend status to backend status
        status_mapping = {
            'active': 'aktif',
            'inactive': 'nonaktif',
            'training': 'cuti'
        }
        backend_status = status_mapping.get(status, status)
        kader_list = kader_list.filter(status=backend_status)
    
    kader_list = kader_list.select_related('penduduk', 'posyandu').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(kader_list, per_page)
    page_obj = paginator.get_page(page)
    
    # Get statistics
    total_kader = PosyanduKader.objects.count()
    active_kader = PosyanduKader.objects.filter(status='aktif').count()
    leader_kader = PosyanduKader.objects.filter(jabatan='ketua', status='aktif').count()
    inactive_kader = PosyanduKader.objects.filter(status='nonaktif').count()
    
    stats = {
        'total_kader': total_kader,
        'active_kader': active_kader,
        'leader_kader': leader_kader,
        'inactive_kader': inactive_kader
    }
    
    # Get posyandu list for filter dropdown
    posyandu_list = PosyanduLocation.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_title': 'Manajemen Kader Posyandu',
        'page_subtitle': 'Kelola data kader posyandu',
        'kader_list': page_obj,
        'stats': stats,
        'posyandu_list': posyandu_list,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
        'paginator': paginator
    }
    return render(request, 'admin/modules/posyandu/kader.html', context)


@login_required
def pengaturan_admin(request):
    """Pengaturan posyandu admin page"""
    context = {
        'page_title': 'Pengaturan Posyandu',
        'page_subtitle': 'Kelola pengaturan dan kader posyandu'
    }
    return render(request, 'admin/modules/posyandu/pengaturan.html', context)

@login_required
def ibu_hamil_admin(request):
    """Ibu Hamil admin page"""
    context = {
        'page_title': 'Input Data Ibu Hamil',
        'page_subtitle': 'Kelola data ibu hamil'
    }
    return render(request, 'admin/modules/posyandu/ibu_hamil.html', context)

@login_required
def view_balita(request):
    """View Balita page"""
    context = {
        'page_title': 'View Data Balita',
        'page_subtitle': 'Lihat dan kelola data balita'
    }
    return render(request, 'admin/modules/posyandu/balita.html', context)

@login_required
def view_lansia(request):
    """View Lansia page"""
    context = {
        'page_title': 'View Data Lansia',
        'page_subtitle': 'Lihat dan kelola data lansia'
    }
    return render(request, 'admin/modules/posyandu/lansia.html', context)

@login_required
def stunting_admin(request):
    """Stunting admin page"""
    context = {
        'page_title': 'Input Data Stunting',
        'page_subtitle': 'Kelola data stunting balita'
    }
    return render(request, 'admin/modules/posyandu/stunting.html', context)


# ============= PEMERIKSAAN IBU HAMIL API VIEWS =============

@login_required
def pemeriksaan_ibu_hamil_list_api(request):
    """List pemeriksaan ibu hamil"""
    ibu_hamil_id = request.GET.get('ibu_hamil_id', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    pemeriksaan = PemeriksaanIbuHamil.objects.all()
    
    if ibu_hamil_id:
        pemeriksaan = pemeriksaan.filter(ibu_hamil_id=ibu_hamil_id)
    
    pemeriksaan = pemeriksaan.select_related('ibu_hamil__penduduk', 'pemeriksa').order_by('-tanggal_periksa')
    
    paginator = Paginator(pemeriksaan, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for p in page_obj:
        data.append({
            'id': p.id,
            'ibu_nama': p.ibu_hamil.penduduk.name,
            'tanggal_periksa': p.tanggal_periksa.strftime('%Y-%m-%d'),
            'usia_kehamilan': p.usia_kehamilan,
            'berat_badan': float(p.berat_badan),
            'tekanan_darah': p.tekanan_darah,
            'hemoglobin': float(p.hemoglobin) if p.hemoglobin else None,
            'tablet_fe': p.tablet_fe,
            'imunisasi_tt': p.imunisasi_tt,
            'keluhan': p.keluhan,
            'pemeriksa': p.pemeriksa.username if p.pemeriksa else '-',
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })


@login_required
@require_http_methods(["POST"])
def pemeriksaan_ibu_hamil_create_api(request):
    """Create pemeriksaan ibu hamil"""
    try:
        data = json.loads(request.body)
        
        ibu_hamil = get_object_or_404(IbuHamil, id=data['ibu_hamil_id'])
        tanggal_periksa = datetime.strptime(data['tanggal_periksa'], '%Y-%m-%d').date()
        
        pemeriksaan = PemeriksaanIbuHamil.objects.create(
            ibu_hamil=ibu_hamil,
            tanggal_periksa=tanggal_periksa,
            usia_kehamilan=data['usia_kehamilan'],
            berat_badan=data['berat_badan'],
            tekanan_darah=data['tekanan_darah'],
            tinggi_fundus=data.get('tinggi_fundus'),
            lingkar_lengan_atas=data.get('lingkar_lengan_atas'),
            hemoglobin=data.get('hemoglobin'),
            protein_urin=data.get('protein_urin', ''),
            tablet_fe=data.get('tablet_fe', False),
            imunisasi_tt=data.get('imunisasi_tt', False),
            keluhan=data.get('keluhan', ''),
            anjuran=data.get('anjuran', ''),
            pemeriksa=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data pemeriksaan berhasil ditambahkan',
            'data': {'id': pemeriksaan.id}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan data pemeriksaan: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["PUT"])
def pemeriksaan_ibu_hamil_update_api(request, pemeriksaan_id):
    """Update pemeriksaan ibu hamil"""
    try:
        pemeriksaan = get_object_or_404(PemeriksaanIbuHamil, id=pemeriksaan_id)
        data = json.loads(request.body)
        
        ibu_hamil = get_object_or_404(IbuHamil, id=data['ibu_hamil_id'])
        tanggal_periksa = datetime.strptime(data['tanggal_periksa'], '%Y-%m-%d').date()
        
        pemeriksaan.ibu_hamil = ibu_hamil
        pemeriksaan.tanggal_periksa = tanggal_periksa
        pemeriksaan.usia_kehamilan = data['usia_kehamilan']
        pemeriksaan.berat_badan = data['berat_badan']
        pemeriksaan.tekanan_darah = data['tekanan_darah']
        pemeriksaan.tinggi_fundus = data.get('tinggi_fundus')
        pemeriksaan.lingkar_lengan_atas = data.get('lingkar_lengan_atas')
        pemeriksaan.hemoglobin = data.get('hemoglobin')
        pemeriksaan.protein_urin = data.get('protein_urin', '')
        pemeriksaan.tablet_fe = data.get('tablet_fe', False)
        pemeriksaan.imunisasi_tt = data.get('imunisasi_tt', False)
        pemeriksaan.keluhan = data.get('keluhan', '')
        pemeriksaan.anjuran = data.get('anjuran', '')
        pemeriksaan.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data pemeriksaan berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui data pemeriksaan: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE"])
def pemeriksaan_ibu_hamil_delete_api(request, pemeriksaan_id):
    """Delete pemeriksaan ibu hamil"""
    try:
        pemeriksaan = get_object_or_404(PemeriksaanIbuHamil, id=pemeriksaan_id)
        ibu_nama = pemeriksaan.ibu_hamil.penduduk.name
        pemeriksaan.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data pemeriksaan "{ibu_nama}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus data pemeriksaan: {str(e)}'
        }, status=400)


# ============= KADER API VIEWS =============

@require_http_methods(["GET"])
def kader_list_api(request):
    """List kader posyandu with pagination and search"""
    search = request.GET.get('search', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    status = request.GET.get('status', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    kaders = PosyanduKader.objects.all()
    
    if search:
        kaders = kaders.filter(
            Q(penduduk__name__icontains=search) |
            Q(penduduk__nik__icontains=search) |
            Q(posyandu__name__icontains=search)
        )
    
    if posyandu_id:
        kaders = kaders.filter(posyandu_id=posyandu_id)
    
    if status:
        kaders = kaders.filter(status=status)
    
    kaders = kaders.select_related('penduduk', 'posyandu').order_by('-created_at')
    
    paginator = Paginator(kaders, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for kader in page_obj:
        data.append({
            'id': kader.id,
            'penduduk_nama': kader.penduduk.name,
            'penduduk_nik': kader.penduduk.nik,
            'posyandu_nama': kader.posyandu.name,
            'jabatan': kader.jabatan,
            'nomor_hp': kader.nomor_hp,
            'tanggal_bergabung': kader.tanggal_mulai.strftime('%Y-%m-%d'),
            'tanggal_selesai': kader.tanggal_selesai.strftime('%Y-%m-%d') if kader.tanggal_selesai else None,
            'status': kader.status,
            'created_at': kader.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })


@login_required
def kader_detail_api(request, kader_id):
    """Get kader detail"""
    kader = get_object_or_404(PosyanduKader, id=kader_id)
    
    data = {
        'id': kader.id,
        'penduduk_id': kader.penduduk.id,
        'penduduk_nama': kader.penduduk.name,
        'penduduk_nik': kader.penduduk.nik,
        'posyandu_id': kader.posyandu.id,
        'posyandu_nama': kader.posyandu.name,
        'jabatan': kader.jabatan,
        'nomor_hp': kader.nomor_hp,
        'tanggal_bergabung': kader.tanggal_mulai.strftime('%Y-%m-%d'),
        'tanggal_selesai': kader.tanggal_selesai.strftime('%Y-%m-%d') if kader.tanggal_selesai else '',
        'status': kader.status,
        'keterangan': kader.keterangan,
        'created_at': kader.created_at.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse({'data': data})


@login_required
@require_http_methods(["POST"])
def kader_create_api(request):
    """Create new kader"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['penduduk_id', 'posyandu_id', 'jabatan', 'tanggal_bergabung']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Field {field} wajib diisi'
                }, status=400)
        
        penduduk = get_object_or_404(Penduduk, id=data['penduduk_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        # Check for existing kader with same penduduk, posyandu, and jabatan
        existing_kader = PosyanduKader.objects.filter(
            penduduk=penduduk,
            posyandu=posyandu,
            jabatan=data['jabatan']
        ).first()
        
        if existing_kader:
            return JsonResponse({
                'success': False,
                'message': f'Kader {penduduk.name} sudah terdaftar sebagai {data["jabatan"]} di {posyandu.name}'
            }, status=400)
        
        tanggal_bergabung = datetime.strptime(data['tanggal_bergabung'], '%Y-%m-%d').date()
        tanggal_selesai = None
        if data.get('tanggal_selesai'):
            tanggal_selesai = datetime.strptime(data['tanggal_selesai'], '%Y-%m-%d').date()
        
        kader = PosyanduKader.objects.create(
            penduduk=penduduk,
            posyandu=posyandu,
            jabatan=data['jabatan'],
            nomor_hp=data.get('nomor_hp', ''),
            tanggal_mulai=tanggal_bergabung,
            tanggal_selesai=tanggal_selesai,
            status=data.get('status', 'aktif'),
            keterangan=data.get('keterangan', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Kader berhasil ditambahkan',
            'data': {'id': kader.id, 'nama': kader.penduduk.name}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan kader: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["PUT"])
def kader_update_api(request, kader_id):
    """Update kader"""
    try:
        kader = get_object_or_404(PosyanduKader, id=kader_id)
        data = json.loads(request.body)
        
        penduduk = get_object_or_404(Penduduk, id=data['penduduk_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        tanggal_bergabung = datetime.strptime(data['tanggal_bergabung'], '%Y-%m-%d').date()
        tanggal_selesai = None
        if data.get('tanggal_selesai'):
            tanggal_selesai = datetime.strptime(data['tanggal_selesai'], '%Y-%m-%d').date()
        
        kader.penduduk = penduduk
        kader.posyandu = posyandu
        kader.jabatan = data['jabatan']
        kader.nomor_hp = data.get('nomor_hp', '')
        kader.tanggal_mulai = tanggal_bergabung
        kader.tanggal_selesai = tanggal_selesai
        kader.status = data.get('status', 'aktif')
        kader.keterangan = data.get('keterangan', '')
        kader.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Kader berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui kader: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE"])
def kader_delete_api(request, kader_id):
    """Delete kader"""
    try:
        kader = get_object_or_404(PosyanduKader, id=kader_id)
        kader_name = kader.penduduk.name
        kader.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Kader "{kader_name}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus kader: {str(e)}'
        }, status=400)


# ============= IBU HAMIL API VIEWS =============

@require_http_methods(["GET"])
def ibu_hamil_list_api(request):
    """List ibu hamil with pagination and search"""
    search = request.GET.get('search', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    risiko = request.GET.get('risiko', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    ibu_hamil = IbuHamil.objects.filter(status_aktif=True)
    
    if search:
        ibu_hamil = ibu_hamil.filter(
            Q(penduduk__name__icontains=search) |
            Q(penduduk__nik__icontains=search) |
            Q(nomor_buku_kia__icontains=search)
        )
    
    if posyandu_id:
        ibu_hamil = ibu_hamil.filter(posyandu_id=posyandu_id)
    
    if risiko:
        ibu_hamil = ibu_hamil.filter(risiko_kehamilan=risiko)
    
    ibu_hamil = ibu_hamil.select_related('penduduk', 'posyandu').order_by('-created_at')
    
    paginator = Paginator(ibu_hamil, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for ibu in page_obj:
        data.append({
            'id': ibu.id,
            'penduduk': {
                'id': ibu.penduduk.id,
                'name': ibu.penduduk.name,
                'nik': ibu.penduduk.nik,
                'birth_date': ibu.penduduk.birth_date.strftime('%Y-%m-%d') if ibu.penduduk.birth_date else None,
            },
            'posyandu': {
                'id': ibu.posyandu.id,
                'name': ibu.posyandu.name,
            },
            'penduduk_id': ibu.penduduk.id,
            'posyandu_id': ibu.posyandu.id,
            'usia_kehamilan': ibu.usia_kehamilan,
            'tanggal_hpht': ibu.tanggal_hpht.strftime('%Y-%m-%d'),
            'tanggal_perkiraan_lahir': ibu.tanggal_perkiraan_lahir.strftime('%Y-%m-%d'),
            'riwayat_kehamilan': ibu.get_riwayat_kehamilan_display(),
            'risiko_kehamilan': ibu.risiko_kehamilan,
            'nomor_buku_kia': ibu.nomor_buku_kia,
            'keterangan': ibu.keterangan,
            'created_at': ibu.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'success': True,
        'data': data,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })


@login_required
def ibu_hamil_detail_api(request, ibu_id):
    """Get ibu hamil detail"""
    ibu = get_object_or_404(IbuHamil, id=ibu_id)
    
    data = {
        'id': ibu.id,
        'penduduk_id': ibu.penduduk.id,
        'nama': ibu.penduduk.name,
        'nik': ibu.penduduk.nik,
        'posyandu_id': ibu.posyandu.id,
        'posyandu_name': ibu.posyandu.name,
        'tanggal_hpht': ibu.tanggal_hpht.strftime('%Y-%m-%d'),
        'usia_kehamilan': ibu.usia_kehamilan,
        'tanggal_perkiraan_lahir': ibu.tanggal_perkiraan_lahir.strftime('%Y-%m-%d'),
        'riwayat_kehamilan': ibu.riwayat_kehamilan,
        'berat_badan_sebelum_hamil': float(ibu.berat_badan_sebelum_hamil) if ibu.berat_badan_sebelum_hamil else None,
        'tinggi_badan': float(ibu.tinggi_badan) if ibu.tinggi_badan else None,
        'golongan_darah': ibu.golongan_darah,
        'riwayat_penyakit': ibu.riwayat_penyakit,
        'risiko_kehamilan': ibu.risiko_kehamilan,
        'nomor_buku_kia': ibu.nomor_buku_kia,
        'keterangan': ibu.keterangan,
        'created_at': ibu.created_at.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse({'data': data})


@login_required
@require_http_methods(["POST"])
def ibu_hamil_create_api(request):
    """Create new ibu hamil"""
    try:
        data = json.loads(request.body)
        
        penduduk = get_object_or_404(Penduduk, id=data['penduduk_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        tanggal_hpht = datetime.strptime(data['tanggal_hpht'], '%Y-%m-%d').date()
        
        ibu = IbuHamil.objects.create(
            penduduk=penduduk,
            posyandu=posyandu,
            tanggal_hpht=tanggal_hpht,
            usia_kehamilan=data['usia_kehamilan'],
            riwayat_kehamilan=data['riwayat_kehamilan'],
            berat_badan_sebelum_hamil=data.get('berat_badan_sebelum_hamil'),
            tinggi_badan=data.get('tinggi_badan'),
            golongan_darah=data.get('golongan_darah', ''),
            riwayat_penyakit=data.get('riwayat_penyakit', ''),
            risiko_kehamilan=data.get('risiko_kehamilan', 'rendah'),
            nomor_buku_kia=data.get('nomor_buku_kia', ''),
            keterangan=data.get('keterangan', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data ibu hamil berhasil ditambahkan',
            'data': {'id': ibu.id, 'nama': ibu.penduduk.name}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan data ibu hamil: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["PUT"])
def ibu_hamil_update_api(request, ibu_id):
    """Update ibu hamil"""
    try:
        ibu = get_object_or_404(IbuHamil, id=ibu_id)
        data = json.loads(request.body)
        
        penduduk = get_object_or_404(Penduduk, id=data['penduduk_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        tanggal_hpht = datetime.strptime(data['tanggal_hpht'], '%Y-%m-%d').date()
        
        ibu.penduduk = penduduk
        ibu.posyandu = posyandu
        ibu.tanggal_hpht = tanggal_hpht
        ibu.usia_kehamilan = data['usia_kehamilan']
        ibu.riwayat_kehamilan = data['riwayat_kehamilan']
        ibu.berat_badan_sebelum_hamil = data.get('berat_badan_sebelum_hamil')
        ibu.tinggi_badan = data.get('tinggi_badan')
        ibu.golongan_darah = data.get('golongan_darah', '')
        ibu.riwayat_penyakit = data.get('riwayat_penyakit', '')
        ibu.risiko_kehamilan = data.get('risiko_kehamilan', 'rendah')
        ibu.nomor_buku_kia = data.get('nomor_buku_kia', '')
        ibu.keterangan = data.get('keterangan', '')
        ibu.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data ibu hamil berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui data ibu hamil: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE"])
def ibu_hamil_delete_api(request, ibu_id):
    """Delete ibu hamil"""
    try:
        ibu = get_object_or_404(IbuHamil, id=ibu_id)
        ibu_name = ibu.penduduk.name
        ibu.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data ibu hamil "{ibu_name}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus data ibu hamil: {str(e)}'
        }, status=400)


# ============= BALITA API VIEWS =============

@require_http_methods(["GET"])
def balita_list_api(request):
    """List balita data using nutrition data"""
    search = request.GET.get('search', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    nutrition_status = request.GET.get('nutrition_status', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    # Get nutrition data (balita records) instead of penduduk
    nutrition_data = NutritionData.objects.select_related('patient', 'posyandu').all()
    
    # Apply filters
    if search:
        nutrition_data = nutrition_data.filter(
            Q(patient__name__icontains=search) |
            Q(patient__nik__icontains=search)
        )
    
    if posyandu_id:
        nutrition_data = nutrition_data.filter(posyandu_id=posyandu_id)
        
    if nutrition_status:
        nutrition_data = nutrition_data.filter(nutrition_status=nutrition_status)
    
    nutrition_data = nutrition_data.order_by('-measurement_date', 'patient__name')
    
    paginator = Paginator(nutrition_data, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for nutrition in page_obj:
        data.append({
            'id': nutrition.id,
            'patient_name': nutrition.patient.name,
            'patient_nik': nutrition.patient.nik,
            'age_months': nutrition.age_months,
            'posyandu_name': nutrition.posyandu.name,
            'nutrition_status': nutrition.nutrition_status,
            'measurement_date': nutrition.measurement_date.strftime('%Y-%m-%d'),
            'weight': float(nutrition.weight) if nutrition.weight else 0,
            'height': float(nutrition.height) if nutrition.height else 0,
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
        }
    })


@require_http_methods(["GET"])
def balita_detail_api(request, balita_id):
    """Get balita detail"""
    nutrition = get_object_or_404(NutritionData, id=balita_id)
    
    data = {
        'id': nutrition.id,
        'patient_id': nutrition.patient.id,
        'nama': nutrition.patient.name,
        'nik': nutrition.patient.nik,
        'posyandu_id': nutrition.posyandu.id,
        'posyandu_name': nutrition.posyandu.name,
        'measurement_date': nutrition.measurement_date.strftime('%Y-%m-%d'),
        'age_months': nutrition.age_months,
        'weight': float(nutrition.weight) if nutrition.weight else None,
        'height': float(nutrition.height) if nutrition.height else None,
        'head_circumference': float(nutrition.head_circumference) if nutrition.head_circumference else None,
        'arm_circumference': float(nutrition.arm_circumference) if nutrition.arm_circumference else None,
        'nutrition_status': nutrition.nutrition_status,
        'vitamin_a_given': nutrition.vitamin_a_given,
        'iron_supplement_given': nutrition.iron_supplement_given,
        'notes': nutrition.notes,
        'created_at': nutrition.created_at.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse({'data': data})


@login_required
@require_http_methods(["POST"])
def balita_create_api(request):
    """Create new balita nutrition data"""
    try:
        # Get data from FormData
        patient = get_object_or_404(Penduduk, id=request.POST.get('patient_id'))
        posyandu = get_object_or_404(PosyanduLocation, id=request.POST.get('posyandu_id'))
        
        measurement_date = datetime.strptime(request.POST.get('measurement_date'), '%Y-%m-%d').date()
        
        nutrition = NutritionData.objects.create(
            patient=patient,
            posyandu=posyandu,
            measurement_date=measurement_date,
            age_months=int(request.POST.get('age_months')),
            weight=float(request.POST.get('weight')),
            height=float(request.POST.get('height')),
            head_circumference=float(request.POST.get('head_circumference')) if request.POST.get('head_circumference') else None,
            arm_circumference=float(request.POST.get('arm_circumference')) if request.POST.get('arm_circumference') else None,
            nutrition_status=request.POST.get('nutrition_status'),
            vitamin_a_given=request.POST.get('vitamin_a_given') == 'true',
            iron_supplement_given=request.POST.get('iron_supplement_given') == 'true',
            notes=request.POST.get('notes', ''),
            recorded_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data balita berhasil ditambahkan',
            'data': {'id': nutrition.id, 'nama': nutrition.patient.name}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan data balita: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["POST"])
def balita_update_api(request, balita_id):
    """Update balita nutrition data"""
    try:
        nutrition = get_object_or_404(NutritionData, id=balita_id)
        
        patient = get_object_or_404(Penduduk, id=request.POST.get('patient_id'))
        posyandu = get_object_or_404(PosyanduLocation, id=request.POST.get('posyandu_id'))
        
        measurement_date = datetime.strptime(request.POST.get('measurement_date'), '%Y-%m-%d').date()
        
        nutrition.patient = patient
        nutrition.posyandu = posyandu
        nutrition.measurement_date = measurement_date
        nutrition.age_months = int(request.POST.get('age_months'))
        nutrition.weight = float(request.POST.get('weight'))
        nutrition.height = float(request.POST.get('height'))
        nutrition.head_circumference = float(request.POST.get('head_circumference')) if request.POST.get('head_circumference') else None
        nutrition.arm_circumference = float(request.POST.get('arm_circumference')) if request.POST.get('arm_circumference') else None
        nutrition.nutrition_status = request.POST.get('nutrition_status')
        nutrition.vitamin_a_given = request.POST.get('vitamin_a_given') == 'true'
        nutrition.iron_supplement_given = request.POST.get('iron_supplement_given') == 'true'
        nutrition.notes = request.POST.get('notes', '')
        nutrition.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data balita berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui data balita: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["POST", "DELETE"])
def balita_delete_api(request, balita_id):
    """Delete balita nutrition data"""
    try:
        nutrition = get_object_or_404(NutritionData, id=balita_id)
        patient_name = nutrition.patient.name
        nutrition.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data balita "{patient_name}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus data balita: {str(e)}'
        }, status=400)


# ============= LANSIA API VIEWS =============

@require_http_methods(["GET"])
def lansia_list_api(request):
    """List lansia data using health records"""
    search = request.GET.get('search', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    # Get lansia from penduduk based on age (60+ years)
    today = date.today()
    lansia = Penduduk.objects.filter(
        birth_date__lte=today.replace(year=today.year-60)
    )
    
    if search:
        lansia = lansia.filter(
            Q(name__icontains=search) |
            Q(nik__icontains=search)
        )
    
    lansia = lansia.order_by('name')
    
    paginator = Paginator(lansia, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for l in page_obj:
        age = 0
        if l.birth_date:
            age = today.year - l.birth_date.year
            if today.month < l.birth_date.month or (today.month == l.birth_date.month and today.day < l.birth_date.day):
                age -= 1
        
        # Get latest health record
        latest_record = HealthRecord.objects.filter(patient=l, patient_type='lansia').first()
        
        # Determine health status based on latest record
        health_status = 'sehat'
        if latest_record:
            if latest_record.diagnosis and latest_record.diagnosis.strip():
                health_status = 'sakit'
            elif latest_record.complaints and latest_record.complaints.strip():
                health_status = 'perlu_perhatian'
        
        data.append({
            'id': l.id,
            'name': l.name,
            'nik': l.nik,
            'birth_date': l.birth_date.strftime('%Y-%m-%d') if l.birth_date else None,
            'age': age,
            'gender': l.gender,
            'posyandu_name': latest_record.posyandu.name if latest_record and latest_record.posyandu else '-',
            'health_status': health_status,
            'weight': float(latest_record.weight) if latest_record and latest_record.weight else None,
            'height': float(latest_record.height) if latest_record and latest_record.height else None,
            'blood_pressure_systolic': latest_record.blood_pressure.split('/')[0] if latest_record and latest_record.blood_pressure and '/' in latest_record.blood_pressure else None,
            'blood_pressure_diastolic': latest_record.blood_pressure.split('/')[1] if latest_record and latest_record.blood_pressure and '/' in latest_record.blood_pressure else None,
            'blood_sugar': float(latest_record.blood_sugar) if latest_record and latest_record.blood_sugar else None,
            'last_checkup': latest_record.visit_date.strftime('%Y-%m-%d') if latest_record else None
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
        }
    })


@login_required
def lansia_detail_api(request, lansia_id):
    """Get lansia detail"""
    try:
        health_record = get_object_or_404(HealthRecord, id=lansia_id)
        
        data = {
            'id': health_record.id,
            'patient_id': health_record.patient.id,
            'nama': health_record.patient.name,
            'nik': health_record.patient.nik,
            'posyandu_id': health_record.posyandu.id,
            'posyandu_name': health_record.posyandu.name,
            'visit_date': health_record.visit_date.strftime('%Y-%m-%d'),
            'weight': float(health_record.weight) if health_record.weight else None,
            'height': float(health_record.height) if health_record.height else None,
            'blood_pressure': health_record.blood_pressure,
            'blood_sugar': float(health_record.blood_sugar) if health_record.blood_sugar else None,
            'cholesterol': float(health_record.cholesterol) if health_record.cholesterol else None,
            'complaints': health_record.complaints,
            'diagnosis': health_record.diagnosis,
            'treatment': health_record.treatment,
            'notes': health_record.notes,
            'created_at': health_record.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal mengambil data lansia: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["POST"])
def lansia_create_api(request):
    """Create new lansia health record"""
    try:
        data = json.loads(request.body)
        
        patient = get_object_or_404(Penduduk, id=data['patient_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d').date()
        
        health_record = HealthRecord.objects.create(
            patient=patient,
            posyandu=posyandu,
            patient_type='lansia',
            visit_date=visit_date,
            weight=data.get('weight'),
            height=data.get('height'),
            blood_pressure=data.get('blood_pressure'),
            blood_sugar=data.get('blood_sugar'),
            cholesterol=data.get('cholesterol'),
            complaints=data.get('complaints', ''),
            diagnosis=data.get('diagnosis', ''),
            treatment=data.get('treatment', ''),
            notes=data.get('notes', ''),
            recorded_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data lansia berhasil ditambahkan',
            'data': {'id': health_record.id, 'nama': health_record.patient.name}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan data lansia: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["PUT"])
def lansia_update_api(request, lansia_id):
    """Update lansia health record"""
    try:
        health_record = get_object_or_404(HealthRecord, id=lansia_id)
        data = json.loads(request.body)
        
        patient = get_object_or_404(Penduduk, id=data['patient_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d').date()
        
        health_record.patient = patient
        health_record.posyandu = posyandu
        health_record.visit_date = visit_date
        health_record.weight = data.get('weight')
        health_record.height = data.get('height')
        health_record.blood_pressure = data.get('blood_pressure')
        health_record.blood_sugar = data.get('blood_sugar')
        health_record.cholesterol = data.get('cholesterol')
        health_record.complaints = data.get('complaints', '')
        health_record.diagnosis = data.get('diagnosis', '')
        health_record.treatment = data.get('treatment', '')
        health_record.notes = data.get('notes', '')
        health_record.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data lansia berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui data lansia: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE"])
def lansia_delete_api(request, lansia_id):
    """Delete lansia health record"""
    try:
        health_record = get_object_or_404(HealthRecord, id=lansia_id)
        patient_name = health_record.patient.name
        health_record.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data lansia "{patient_name}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus data lansia: {str(e)}'
        }, status=400)


# ============= STUNTING API VIEWS =============

@require_http_methods(["GET"])
def stunting_list_api(request):
    """List stunting data with pagination and search"""
    search = request.GET.get('search', '')
    posyandu_id = request.GET.get('posyandu_id', '')
    status_stunting = request.GET.get('status_stunting', '')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    stunting_data = StuntingData.objects.all()
    
    if search:
        stunting_data = stunting_data.filter(
            Q(balita__name__icontains=search) |
            Q(balita__nik__icontains=search)
        )
    
    if posyandu_id:
        stunting_data = stunting_data.filter(posyandu_id=posyandu_id)
    
    if status_stunting:
        stunting_data = stunting_data.filter(status_stunting=status_stunting)
    
    stunting_data = stunting_data.select_related('balita', 'posyandu', 'recorded_by').order_by('-tanggal_ukur')
    
    paginator = Paginator(stunting_data, per_page)
    page_obj = paginator.get_page(page)
    
    data = []
    for stunting in page_obj:
        data.append({
            'id': stunting.id,
            'child_name': stunting.balita.name,
            'child_nik': stunting.balita.nik,
            'posyandu_name': stunting.posyandu.name,
            'measurement_date': stunting.tanggal_ukur.strftime('%Y-%m-%d'),
            'age_months': stunting.usia_bulan,
            'height': float(stunting.tinggi_badan),
            'weight': float(stunting.berat_badan),
            'z_score_height_age': float(stunting.z_score_tb_u),
            'stunting_severity': stunting.status_stunting,
            'exclusive_breastfeeding': stunting.asi_eksklusif,
            'low_birth_weight_history': stunting.riwayat_bblr,
            'intervention_status': stunting.intervensi_diberikan,
            'follow_up_date': stunting.follow_up_date.strftime('%Y-%m-%d') if stunting.follow_up_date else None,
            'recorded_by': stunting.recorded_by.username if stunting.recorded_by else '-',
            'created_at': stunting.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
        }
    })


@login_required
def stunting_detail_api(request, stunting_id):
    """Get stunting detail"""
    stunting = get_object_or_404(StuntingData, id=stunting_id)
    
    data = {
        'id': stunting.id,
        'balita_id': stunting.balita.id,
        'nama_balita': stunting.balita.name,
        'nik_balita': stunting.balita.nik,
        'posyandu_id': stunting.posyandu.id,
        'posyandu_name': stunting.posyandu.name,
        'tanggal_ukur': stunting.tanggal_ukur.strftime('%Y-%m-%d'),
        'usia_bulan': stunting.usia_bulan,
        'tinggi_badan': float(stunting.tinggi_badan),
        'berat_badan': float(stunting.berat_badan),
        'z_score_tb_u': float(stunting.z_score_tb_u),
        'z_score_bb_u': float(stunting.z_score_bb_u) if stunting.z_score_bb_u else None,
        'z_score_bb_tb': float(stunting.z_score_bb_tb) if stunting.z_score_bb_tb else None,
        'status_stunting': stunting.status_stunting,
        'asi_eksklusif': stunting.asi_eksklusif,
        'riwayat_bblr': stunting.riwayat_bblr,
        'riwayat_penyakit': stunting.riwayat_penyakit,
        'intervensi_diberikan': stunting.intervensi_diberikan,
        'hasil_intervensi': stunting.hasil_intervensi,
        'follow_up_date': stunting.follow_up_date.strftime('%Y-%m-%d') if stunting.follow_up_date else '',
        'keterangan': stunting.keterangan,
        'created_at': stunting.created_at.strftime('%Y-%m-%d %H:%M')
    }
    
    return JsonResponse({'data': data})


@login_required
@require_http_methods(["POST"])
def stunting_create_api(request):
    """Create new stunting data"""
    try:
        data = json.loads(request.body)
        
        balita = get_object_or_404(Penduduk, id=data['balita_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        tanggal_ukur = datetime.strptime(data['tanggal_ukur'], '%Y-%m-%d').date()
        follow_up_date = None
        if data.get('follow_up_date'):
            follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
        
        stunting = StuntingData.objects.create(
            balita=balita,
            posyandu=posyandu,
            tanggal_ukur=tanggal_ukur,
            usia_bulan=data['usia_bulan'],
            tinggi_badan=data['tinggi_badan'],
            berat_badan=data['berat_badan'],
            z_score_tb_u=data['z_score_tb_u'],
            z_score_bb_u=data.get('z_score_bb_u'),
            z_score_bb_tb=data.get('z_score_bb_tb'),
            status_stunting=data['status_stunting'],
            asi_eksklusif=data.get('asi_eksklusif', False),
            riwayat_bblr=data.get('riwayat_bblr', False),
            riwayat_penyakit=data.get('riwayat_penyakit', ''),
            intervensi_diberikan=data.get('intervensi_diberikan', ''),
            hasil_intervensi=data.get('hasil_intervensi', ''),
            follow_up_date=follow_up_date,
            keterangan=data.get('keterangan', ''),
            recorded_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data stunting berhasil ditambahkan',
            'data': {'id': stunting.id, 'nama': stunting.balita.name}
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menambahkan data stunting: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["PUT"])
def stunting_update_api(request, stunting_id):
    """Update stunting data"""
    try:
        stunting = get_object_or_404(StuntingData, id=stunting_id)
        data = json.loads(request.body)
        
        balita = get_object_or_404(Penduduk, id=data['balita_id'])
        posyandu = get_object_or_404(PosyanduLocation, id=data['posyandu_id'])
        
        tanggal_ukur = datetime.strptime(data['tanggal_ukur'], '%Y-%m-%d').date()
        follow_up_date = None
        if data.get('follow_up_date'):
            follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
        
        stunting.balita = balita
        stunting.posyandu = posyandu
        stunting.tanggal_ukur = tanggal_ukur
        stunting.usia_bulan = data['usia_bulan']
        stunting.tinggi_badan = data['tinggi_badan']
        stunting.berat_badan = data['berat_badan']
        stunting.z_score_tb_u = data['z_score_tb_u']
        stunting.z_score_bb_u = data.get('z_score_bb_u')
        stunting.z_score_bb_tb = data.get('z_score_bb_tb')
        stunting.status_stunting = data['status_stunting']
        stunting.asi_eksklusif = data.get('asi_eksklusif', False)
        stunting.riwayat_bblr = data.get('riwayat_bblr', False)
        stunting.riwayat_penyakit = data.get('riwayat_penyakit', '')
        stunting.intervensi_diberikan = data.get('intervensi_diberikan', '')
        stunting.hasil_intervensi = data.get('hasil_intervensi', '')
        stunting.follow_up_date = follow_up_date
        stunting.keterangan = data.get('keterangan', '')
        stunting.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data stunting berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal memperbarui data stunting: {str(e)}'
        }, status=400)


@login_required
@require_http_methods(["DELETE"])
def stunting_delete_api(request, stunting_id):
    """Delete stunting data"""
    try:
        stunting = get_object_or_404(StuntingData, id=stunting_id)
        balita_name = stunting.balita.name
        stunting.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Data stunting "{balita_name}" berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Gagal menghapus data stunting: {str(e)}'
        }, status=400)


@login_required
def penduduk_admin(request):
    """Data penduduk admin page"""
    context = {
        'page_title': 'Data Penduduk',
        'page_subtitle': 'Kelola data penduduk untuk posyandu'
    }
    return render(request, 'admin/modules/posyandu/penduduk.html', context)


@login_required
def penduduk_list_api(request):
    """API untuk mengambil data penduduk dengan pencarian"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        dusun_id = request.GET.get('dusun_id', '')
        gender = request.GET.get('gender', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Get penduduk data
        penduduk_list = Penduduk.objects.select_related('dusun', 'lorong').all()
        
        # Apply filters
        if search:
            penduduk_list = penduduk_list.filter(
                Q(name__icontains=search) |
                Q(nik__icontains=search)
            )
        
        if dusun_id:
            penduduk_list = penduduk_list.filter(dusun_id=dusun_id)
            
        if gender:
            penduduk_list = penduduk_list.filter(gender=gender)
        
        # Order by name
        penduduk_list = penduduk_list.order_by('name')
        
        # Pagination
        paginator = Paginator(penduduk_list, per_page)
        page_obj = paginator.get_page(page)
        
        # Prepare data
        data = []
        for penduduk in page_obj:
            data.append({
                'id': penduduk.id,
                'nik': penduduk.nik,
                'name': penduduk.name,
                'birth_place': penduduk.birth_place,
                'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else '',
                'gender': penduduk.get_gender_display(),
                'religion': penduduk.get_religion_display(),
                'education': penduduk.get_education_display(),
                'occupation': penduduk.occupation,
                'marital_status': penduduk.get_marital_status_display(),
                'dusun': penduduk.dusun.name if penduduk.dusun else '',
                'lorong': penduduk.lorong.name if penduduk.lorong else '',
                'address': penduduk.address,
                'phone': penduduk.phone_number or penduduk.mobile_number,
                'email': penduduk.email,
                'is_active': penduduk.is_active,
            })
        
        return JsonResponse({
            'success': True,
            'data': data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'per_page': per_page
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def penduduk_detail_api(request, penduduk_id):
    """API untuk mengambil detail penduduk"""
    try:
        penduduk = get_object_or_404(Penduduk, id=penduduk_id)
        
        data = {
            'id': penduduk.id,
            'nik': penduduk.nik,
            'name': penduduk.name,
            'birth_place': penduduk.birth_place,
            'birth_date': penduduk.birth_date.strftime('%Y-%m-%d') if penduduk.birth_date else '',
            'gender': penduduk.get_gender_display(),
            'religion': penduduk.get_religion_display(),
            'education': penduduk.get_education_display(),
            'occupation': penduduk.occupation,
            'marital_status': penduduk.get_marital_status_display(),
            'blood_type': penduduk.get_blood_type_display(),
            'height': penduduk.height,
            'weight': penduduk.weight,
            'dusun': penduduk.dusun.name if penduduk.dusun else '',
            'lorong': penduduk.lorong.name if penduduk.lorong else '',
            'address': penduduk.address,
            'phone': penduduk.phone_number or penduduk.mobile_number,
            'email': penduduk.email,
            'emergency_contact_name': penduduk.emergency_contact,
            'emergency_contact_phone': penduduk.emergency_phone,
            'is_active': penduduk.is_active,
            'created_at': penduduk.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(penduduk, 'created_at') else '',
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def get_dusun_dropdown(request):
    """API untuk dropdown dusun"""
    try:
        dusun_list = Dusun.objects.all().order_by('name')
        data = [{'id': dusun.id, 'name': dusun.name} for dusun in dusun_list]
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def penduduk_create_api(request):
    """API untuk membuat data penduduk baru"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validasi data minimal
        required_fields = ['name', 'nik', 'gender']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False, 
                    'error': f'Field {field} is required'
                }, status=400)
        
        # Cek NIK unik
        if Penduduk.objects.filter(nik=data['nik']).exists():
            return JsonResponse({
                'success': False, 
                'error': 'NIK sudah terdaftar'
            }, status=400)
        
        # Buat penduduk baru
        penduduk = Penduduk(
            nik=data['nik'],
            name=data['name'],
            gender=data['gender'],
            birth_place=data.get('birth_place', ''),
            birth_date=data.get('birth_date') and datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
            religion=data.get('religion', ''),
            education=data.get('education', ''),
            occupation=data.get('occupation', ''),
            marital_status=data.get('marital_status', ''),
            blood_type=data.get('blood_type', ''),
            height=data.get('height'),
            weight=data.get('weight'),
            address=data.get('address', ''),
            phone_number=data.get('phone', ''),
            email=data.get('email', ''),
            emergency_contact=data.get('emergency_contact_name', ''),
            emergency_phone=data.get('emergency_contact_phone', ''),
            is_active=True
        )
        
        # Set dusun jika ada
        if data.get('dusun_id'):
            try:
                penduduk.dusun = Dusun.objects.get(id=data['dusun_id'])
            except Dusun.DoesNotExist:
                pass
        
        # Set lorong jika ada
        if data.get('lorong_id'):
            try:
                penduduk.lorong = Lorong.objects.get(id=data['lorong_id'])
            except Lorong.DoesNotExist:
                pass
        
        penduduk.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data penduduk berhasil ditambahkan',
            'id': penduduk.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def penduduk_update_api(request, penduduk_id):
    """API untuk memperbarui data penduduk"""
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        penduduk = get_object_or_404(Penduduk, id=penduduk_id)
        data = json.loads(request.body)
        
        # Validasi data minimal
        required_fields = ['name', 'nik', 'gender']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False, 
                    'error': f'Field {field} is required'
                }, status=400)
        
        # Cek NIK unik jika berubah
        if data['nik'] != penduduk.nik and Penduduk.objects.filter(nik=data['nik']).exists():
            return JsonResponse({
                'success': False, 
                'error': 'NIK sudah terdaftar'
            }, status=400)
        
        # Update data penduduk
        penduduk.nik = data['nik']
        penduduk.name = data['name']
        penduduk.gender = data['gender']
        penduduk.birth_place = data.get('birth_place', penduduk.birth_place)
        
        if data.get('birth_date'):
            penduduk.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        
        penduduk.religion = data.get('religion', penduduk.religion)
        penduduk.education = data.get('education', penduduk.education)
        penduduk.occupation = data.get('occupation', penduduk.occupation)
        penduduk.marital_status = data.get('marital_status', penduduk.marital_status)
        penduduk.blood_type = data.get('blood_type', penduduk.blood_type)
        penduduk.height = data.get('height', penduduk.height)
        penduduk.weight = data.get('weight', penduduk.weight)
        penduduk.address = data.get('address', penduduk.address)
        penduduk.phone_number = data.get('phone', penduduk.phone_number)
        penduduk.email = data.get('email', penduduk.email)
        penduduk.emergency_contact = data.get('emergency_contact_name', penduduk.emergency_contact)
        penduduk.emergency_phone = data.get('emergency_contact_phone', penduduk.emergency_phone)
        
        # Update dusun jika ada
        if data.get('dusun_id'):
            try:
                penduduk.dusun = Dusun.objects.get(id=data['dusun_id'])
            except Dusun.DoesNotExist:
                pass
        
        # Update lorong jika ada
        if data.get('lorong_id'):
            try:
                penduduk.lorong = Lorong.objects.get(id=data['lorong_id'])
            except Lorong.DoesNotExist:
                pass
        
        penduduk.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data penduduk berhasil diperbarui'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def penduduk_delete_api(request, penduduk_id):
    """API untuk menghapus data penduduk"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        penduduk = get_object_or_404(Penduduk, id=penduduk_id)
        
        # Soft delete (set is_active = False)
        penduduk.is_active = False
        penduduk.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data penduduk berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
