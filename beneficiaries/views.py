from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils.dateparse import parse_date
from django.utils.text import slugify
import json
import csv
from datetime import datetime, date
from decimal import Decimal
from io import StringIO

from .models import (
    BeneficiaryCategory, Beneficiary, Aid, AidDistribution, BeneficiaryVerification,
    TarafKehidupan, DataBantuan, DokumenGampong, Berita, LetterTemplate, Surat
)
from references.models import Penduduk
from django.contrib.auth import get_user_model

User = get_user_model()

# ============ BENEFICIARY CATEGORIES ============

def beneficiary_categories_list(request):
    """List beneficiary categories with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    is_active = request.GET.get('is_active', '')
    
    categories = BeneficiaryCategory.objects.all()
    
    # Apply filters
    if search:
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    if is_active:
        categories = categories.filter(is_active=is_active.lower() == 'true')
    
    categories = categories.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(categories, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for category in page_obj:
        beneficiaries_count = category.beneficiary_set.count()
        data.append({
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'criteria': category.criteria,
            'beneficiaries_count': beneficiaries_count,
            'is_active': category.is_active,
            'created_at': category.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def beneficiary_category_create(request):
    """Create new beneficiary category"""
    try:
        data = json.loads(request.body)
        
        category = BeneficiaryCategory.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            criteria=data.get('criteria', ''),
            is_active=data.get('is_active', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Kategori berhasil dibuat',
            'data': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'criteria': category.criteria,
                'is_active': category.is_active,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def beneficiary_category_detail(request, category_id):
    """Get beneficiary category details"""
    try:
        category = get_object_or_404(BeneficiaryCategory, id=category_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'criteria': category.criteria,
                'is_active': category.is_active,
                'created_at': category.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': category.updated_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def beneficiary_category_update(request, category_id):
    """Update beneficiary category"""
    try:
        category = get_object_or_404(BeneficiaryCategory, id=category_id)
        data = json.loads(request.body)
        
        category.name = data.get('name', category.name)
        category.description = data.get('description', category.description)
        category.criteria = data.get('criteria', category.criteria)
        category.is_active = data.get('is_active', category.is_active)
        category.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Kategori berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def beneficiary_category_delete(request, category_id):
    """Delete beneficiary category"""
    try:
        category = get_object_or_404(BeneficiaryCategory, id=category_id)
        category.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Kategori berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ BENEFICIARIES ============

def beneficiaries_list(request):
    """List beneficiaries with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    category_id = request.GET.get('category_id', '')
    status = request.GET.get('status', '')
    economic_status = request.GET.get('economic_status', '')
    
    beneficiaries = Beneficiary.objects.select_related('person', 'category', 'registered_by').all()
    
    # Apply filters
    if search:
        beneficiaries = beneficiaries.filter(
            Q(person__nama__icontains=search) |
            Q(person__nik__icontains=search) |
            Q(category__name__icontains=search)
        )
    
    if category_id:
        beneficiaries = beneficiaries.filter(category_id=category_id)
    
    if status:
        beneficiaries = beneficiaries.filter(status=status)
    
    if economic_status:
        beneficiaries = beneficiaries.filter(economic_status=economic_status)
    
    beneficiaries = beneficiaries.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(beneficiaries, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for beneficiary in page_obj:
        data.append({
            'id': beneficiary.id,
            'person_name': beneficiary.person.nama,
            'person_nik': beneficiary.person.nik,
            'category_name': beneficiary.category.name,
            'registration_date': beneficiary.registration_date.strftime('%Y-%m-%d'),
            'status': beneficiary.get_status_display(),
            'economic_status': beneficiary.get_economic_status_display(),
            'monthly_income': float(beneficiary.monthly_income) if beneficiary.monthly_income else 0,
            'family_members_count': beneficiary.family_members_count,
            'verification_date': beneficiary.verification_date.strftime('%Y-%m-%d') if beneficiary.verification_date else None,
            'registered_by': beneficiary.registered_by.username if beneficiary.registered_by else None,
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def beneficiary_create(request):
    """Create new beneficiary"""
    try:
        data = json.loads(request.body)
        
        person = get_object_or_404(Penduduk, id=data['person_id'])
        category = get_object_or_404(BeneficiaryCategory, id=data['category_id'])
        
        beneficiary = Beneficiary.objects.create(
            person=person,
            category=category,
            registration_date=parse_date(data['registration_date']),
            status=data.get('status', 'aktif'),
            economic_status=data['economic_status'],
            monthly_income=Decimal(str(data.get('monthly_income', 0))),
            family_members_count=data.get('family_members_count', 1),
            house_condition=data.get('house_condition', ''),
            special_needs=data.get('special_needs', ''),
            verification_date=parse_date(data['verification_date']) if data.get('verification_date') else None,
            notes=data.get('notes', ''),
            registered_by_id=data.get('registered_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Penerima bantuan berhasil didaftarkan',
            'data': {
                'id': beneficiary.id,
                'person_name': beneficiary.person.nama,
                'category_name': beneficiary.category.name,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def beneficiary_detail(request, beneficiary_id):
    """Get beneficiary details"""
    try:
        beneficiary = get_object_or_404(Beneficiary.objects.select_related('person', 'category', 'registered_by'), id=beneficiary_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': beneficiary.id,
                'person': {
                    'id': beneficiary.person.id,
                    'nama': beneficiary.person.nama,
                    'nik': beneficiary.person.nik,
                    'tempat_lahir': beneficiary.person.tempat_lahir,
                    'tanggal_lahir': beneficiary.person.tanggal_lahir.strftime('%Y-%m-%d'),
                    'jenis_kelamin': beneficiary.person.jenis_kelamin,
                },
                'category': {
                    'id': beneficiary.category.id,
                    'name': beneficiary.category.name,
                },
                'registration_date': beneficiary.registration_date.strftime('%Y-%m-%d'),
                'status': beneficiary.status,
                'economic_status': beneficiary.economic_status,
                'monthly_income': float(beneficiary.monthly_income) if beneficiary.monthly_income else 0,
                'family_members_count': beneficiary.family_members_count,
                'house_condition': beneficiary.house_condition,
                'special_needs': beneficiary.special_needs,
                'verification_date': beneficiary.verification_date.strftime('%Y-%m-%d') if beneficiary.verification_date else None,
                'notes': beneficiary.notes,
                'registered_by': beneficiary.registered_by.username if beneficiary.registered_by else None,
                'created_at': beneficiary.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': beneficiary.updated_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def beneficiary_update(request, beneficiary_id):
    """Update beneficiary"""
    try:
        beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
        data = json.loads(request.body)
        
        if 'person_id' in data:
            beneficiary.person = get_object_or_404(Penduduk, id=data['person_id'])
        if 'category_id' in data:
            beneficiary.category = get_object_or_404(BeneficiaryCategory, id=data['category_id'])
        if 'registration_date' in data:
            beneficiary.registration_date = parse_date(data['registration_date'])
        if 'status' in data:
            beneficiary.status = data['status']
        if 'economic_status' in data:
            beneficiary.economic_status = data['economic_status']
        if 'monthly_income' in data:
            beneficiary.monthly_income = Decimal(str(data['monthly_income']))
        if 'family_members_count' in data:
            beneficiary.family_members_count = data['family_members_count']
        if 'house_condition' in data:
            beneficiary.house_condition = data['house_condition']
        if 'special_needs' in data:
            beneficiary.special_needs = data['special_needs']
        if 'verification_date' in data:
            beneficiary.verification_date = parse_date(data['verification_date']) if data['verification_date'] else None
        if 'notes' in data:
            beneficiary.notes = data['notes']
        
        beneficiary.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data penerima bantuan berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def beneficiary_delete(request, beneficiary_id):
    """Delete beneficiary"""
    try:
        beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
        beneficiary.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Data penerima bantuan berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ AIDS ============

def aids_list(request):
    """List aids with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    aid_type = request.GET.get('aid_type', '')
    source = request.GET.get('source', '')
    is_active = request.GET.get('is_active', '')
    
    aids = Aid.objects.select_related('created_by').all()
    
    # Apply filters
    if search:
        aids = aids.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    if aid_type:
        aids = aids.filter(aid_type=aid_type)
    
    if source:
        aids = aids.filter(source=source)
    
    if is_active:
        aids = aids.filter(is_active=is_active.lower() == 'true')
    
    aids = aids.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(aids, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for aid in page_obj:
        distributed_count = aid.distributions.filter(status='distributed').count()
        total_distributed = aid.distributions.filter(status='distributed').aggregate(total=Sum('amount_received'))['total'] or 0
        
        data.append({
            'id': aid.id,
            'name': aid.name,
            'aid_type': aid.get_aid_type_display(),
            'source': aid.get_source_display(),
            'value_per_beneficiary': float(aid.value_per_beneficiary),
            'total_budget': float(aid.total_budget),
            'target_beneficiaries': aid.target_beneficiaries,
            'distributed_count': distributed_count,
            'total_distributed': float(total_distributed),
            'start_date': aid.start_date.strftime('%Y-%m-%d'),
            'end_date': aid.end_date.strftime('%Y-%m-%d'),
            'is_active': aid.is_active,
            'created_by': aid.created_by.username if aid.created_by else None,
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def aid_create(request):
    """Create new aid"""
    try:
        data = json.loads(request.body)
        
        aid = Aid.objects.create(
            name=data['name'],
            aid_type=data['aid_type'],
            source=data['source'],
            description=data.get('description', ''),
            value_per_beneficiary=Decimal(str(data['value_per_beneficiary'])),
            total_budget=Decimal(str(data['total_budget'])),
            target_beneficiaries=data['target_beneficiaries'],
            start_date=parse_date(data['start_date']),
            end_date=parse_date(data['end_date']),
            requirements=data.get('requirements', ''),
            is_active=data.get('is_active', True),
            created_by_id=data.get('created_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Program bantuan berhasil dibuat',
            'data': {
                'id': aid.id,
                'name': aid.name,
                'aid_type': aid.get_aid_type_display(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def aid_detail(request, aid_id):
    """Get aid details"""
    try:
        aid = get_object_or_404(Aid.objects.select_related('created_by'), id=aid_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': aid.id,
                'name': aid.name,
                'aid_type': aid.aid_type,
                'source': aid.source,
                'description': aid.description,
                'value_per_beneficiary': float(aid.value_per_beneficiary),
                'total_budget': float(aid.total_budget),
                'target_beneficiaries': aid.target_beneficiaries,
                'start_date': aid.start_date.strftime('%Y-%m-%d'),
                'end_date': aid.end_date.strftime('%Y-%m-%d'),
                'requirements': aid.requirements,
                'is_active': aid.is_active,
                'created_by': aid.created_by.username if aid.created_by else None,
                'created_at': aid.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': aid.updated_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def aid_update(request, aid_id):
    """Update aid"""
    try:
        aid = get_object_or_404(Aid, id=aid_id)
        data = json.loads(request.body)
        
        aid.name = data.get('name', aid.name)
        aid.aid_type = data.get('aid_type', aid.aid_type)
        aid.source = data.get('source', aid.source)
        aid.description = data.get('description', aid.description)
        aid.value_per_beneficiary = Decimal(str(data.get('value_per_beneficiary', aid.value_per_beneficiary)))
        aid.total_budget = Decimal(str(data.get('total_budget', aid.total_budget)))
        aid.target_beneficiaries = data.get('target_beneficiaries', aid.target_beneficiaries)
        aid.start_date = parse_date(data.get('start_date', aid.start_date.strftime('%Y-%m-%d')))
        aid.end_date = parse_date(data.get('end_date', aid.end_date.strftime('%Y-%m-%d')))
        aid.requirements = data.get('requirements', aid.requirements)
        aid.is_active = data.get('is_active', aid.is_active)
        aid.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Program bantuan berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def aid_delete(request, aid_id):
    """Delete aid"""
    try:
        aid = get_object_or_404(Aid, id=aid_id)
        aid.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Program bantuan berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ AID DISTRIBUTIONS ============

def aid_distributions_list(request):
    """List aid distributions with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    aid_id = request.GET.get('aid_id', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    distributions = AidDistribution.objects.select_related('aid', 'beneficiary__person', 'distributed_by').all()
    
    # Apply filters
    if search:
        distributions = distributions.filter(
            Q(beneficiary__person__nama__icontains=search) |
            Q(beneficiary__person__nik__icontains=search) |
            Q(aid__name__icontains=search) |
            Q(receipt_number__icontains=search)
        )
    
    if aid_id:
        distributions = distributions.filter(aid_id=aid_id)
    
    if status:
        distributions = distributions.filter(status=status)
    
    if start_date:
        distributions = distributions.filter(distribution_date__gte=parse_date(start_date))
    
    if end_date:
        distributions = distributions.filter(distribution_date__lte=parse_date(end_date))
    
    distributions = distributions.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(distributions, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for distribution in page_obj:
        data.append({
            'id': distribution.id,
            'aid_name': distribution.aid.name,
            'beneficiary_name': distribution.beneficiary.person.nama,
            'beneficiary_nik': distribution.beneficiary.person.nik,
            'distribution_date': distribution.distribution_date.strftime('%Y-%m-%d') if distribution.distribution_date else None,
            'amount_received': float(distribution.amount_received),
            'status': distribution.get_status_display(),
            'receipt_number': distribution.receipt_number,
            'distributed_by': distribution.distributed_by.username if distribution.distributed_by else None,
            'created_at': distribution.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def aid_distribution_create(request):
    """Create new aid distribution"""
    try:
        data = json.loads(request.body)
        
        aid = get_object_or_404(Aid, id=data['aid_id'])
        beneficiary = get_object_or_404(Beneficiary, id=data['beneficiary_id'])
        
        distribution = AidDistribution.objects.create(
            aid=aid,
            beneficiary=beneficiary,
            distribution_date=parse_date(data['distribution_date']) if data.get('distribution_date') else None,
            amount_received=Decimal(str(data['amount_received'])),
            status=data.get('status', 'pending'),
            receipt_number=data.get('receipt_number', ''),
            notes=data.get('notes', ''),
            distributed_by_id=data.get('distributed_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Distribusi bantuan berhasil dicatat',
            'data': {
                'id': distribution.id,
                'aid_name': distribution.aid.name,
                'beneficiary_name': distribution.beneficiary.person.nama,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def aid_distribution_detail(request, distribution_id):
    """Get aid distribution details"""
    try:
        distribution = get_object_or_404(AidDistribution.objects.select_related('aid', 'beneficiary__person', 'distributed_by'), id=distribution_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': distribution.id,
                'aid': {
                    'id': distribution.aid.id,
                    'name': distribution.aid.name,
                    'aid_type': distribution.aid.get_aid_type_display(),
                },
                'beneficiary': {
                    'id': distribution.beneficiary.id,
                    'person_name': distribution.beneficiary.person.nama,
                    'person_nik': distribution.beneficiary.person.nik,
                    'category': distribution.beneficiary.category.name,
                },
                'distribution_date': distribution.distribution_date.strftime('%Y-%m-%d') if distribution.distribution_date else None,
                'amount_received': float(distribution.amount_received),
                'status': distribution.status,
                'receipt_number': distribution.receipt_number,
                'notes': distribution.notes,
                'distributed_by': distribution.distributed_by.username if distribution.distributed_by else None,
                'created_at': distribution.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': distribution.updated_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def aid_distribution_update(request, distribution_id):
    """Update aid distribution"""
    try:
        distribution = get_object_or_404(AidDistribution, id=distribution_id)
        data = json.loads(request.body)
        
        if 'aid_id' in data:
            distribution.aid = get_object_or_404(Aid, id=data['aid_id'])
        if 'beneficiary_id' in data:
            distribution.beneficiary = get_object_or_404(Beneficiary, id=data['beneficiary_id'])
        if 'distribution_date' in data:
            distribution.distribution_date = parse_date(data['distribution_date']) if data['distribution_date'] else None
        if 'amount_received' in data:
            distribution.amount_received = Decimal(str(data['amount_received']))
        if 'status' in data:
            distribution.status = data['status']
        if 'receipt_number' in data:
            distribution.receipt_number = data['receipt_number']
        if 'notes' in data:
            distribution.notes = data['notes']
        if 'distributed_by_id' in data:
            distribution.distributed_by_id = data['distributed_by_id']
        
        distribution.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data distribusi bantuan berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def aid_distribution_delete(request, distribution_id):
    """Delete aid distribution"""
    try:
        distribution = get_object_or_404(AidDistribution, id=distribution_id)
        distribution.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Data distribusi bantuan berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ BENEFICIARY VERIFICATIONS ============

def beneficiary_verifications_list(request):
    """List beneficiary verifications with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    beneficiary_id = request.GET.get('beneficiary_id', '')
    verification_status = request.GET.get('verification_status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    verifications = BeneficiaryVerification.objects.select_related('beneficiary__person', 'verifier').all()
    
    # Apply filters
    if search:
        verifications = verifications.filter(
            Q(beneficiary__person__nama__icontains=search) |
            Q(beneficiary__person__nik__icontains=search) |
            Q(verification_notes__icontains=search)
        )
    
    if beneficiary_id:
        verifications = verifications.filter(beneficiary_id=beneficiary_id)
    
    if verification_status:
        verifications = verifications.filter(verification_status=verification_status)
    
    if start_date:
        verifications = verifications.filter(verification_date__gte=parse_date(start_date))
    
    if end_date:
        verifications = verifications.filter(verification_date__lte=parse_date(end_date))
    
    verifications = verifications.order_by('-verification_date')
    
    # Pagination
    paginator = Paginator(verifications, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for verification in page_obj:
        data.append({
            'id': verification.id,
            'beneficiary_name': verification.beneficiary.person.nama,
            'beneficiary_nik': verification.beneficiary.person.nik,
            'verification_date': verification.verification_date.strftime('%Y-%m-%d'),
            'verification_status': verification.get_verification_status_display(),
            'verifier': verification.verifier.username if verification.verifier else None,
            'field_visit_conducted': verification.field_visit_conducted,
            'next_verification_date': verification.next_verification_date.strftime('%Y-%m-%d') if verification.next_verification_date else None,
            'created_at': verification.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def beneficiary_verification_create(request):
    """Create new beneficiary verification"""
    try:
        data = json.loads(request.body)
        
        beneficiary = get_object_or_404(Beneficiary, id=data['beneficiary_id'])
        
        verification = BeneficiaryVerification.objects.create(
            beneficiary=beneficiary,
            verification_date=parse_date(data['verification_date']),
            verification_status=data['verification_status'],
            verifier_id=data.get('verifier_id'),
            verification_notes=data.get('verification_notes', ''),
            documents_checked=data.get('documents_checked', ''),
            field_visit_conducted=data.get('field_visit_conducted', False),
            field_visit_notes=data.get('field_visit_notes', ''),
            next_verification_date=parse_date(data['next_verification_date']) if data.get('next_verification_date') else None
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Verifikasi penerima bantuan berhasil dicatat',
            'data': {
                'id': verification.id,
                'beneficiary_name': verification.beneficiary.person.nama,
                'verification_status': verification.get_verification_status_display(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def beneficiary_verification_detail(request, verification_id):
    """Get beneficiary verification details"""
    try:
        verification = get_object_or_404(BeneficiaryVerification.objects.select_related('beneficiary__person', 'verifier'), id=verification_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': verification.id,
                'beneficiary': {
                    'id': verification.beneficiary.id,
                    'person_name': verification.beneficiary.person.nama,
                    'person_nik': verification.beneficiary.person.nik,
                    'category': verification.beneficiary.category.name,
                },
                'verification_date': verification.verification_date.strftime('%Y-%m-%d'),
                'verification_status': verification.verification_status,
                'verifier': verification.verifier.username if verification.verifier else None,
                'verification_notes': verification.verification_notes,
                'documents_checked': verification.documents_checked,
                'field_visit_conducted': verification.field_visit_conducted,
                'field_visit_notes': verification.field_visit_notes,
                'next_verification_date': verification.next_verification_date.strftime('%Y-%m-%d') if verification.next_verification_date else None,
                'created_at': verification.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': verification.updated_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def beneficiary_verification_update(request, verification_id):
    """Update beneficiary verification"""
    try:
        verification = get_object_or_404(BeneficiaryVerification, id=verification_id)
        data = json.loads(request.body)
        
        if 'beneficiary_id' in data:
            verification.beneficiary = get_object_or_404(Beneficiary, id=data['beneficiary_id'])
        if 'verification_date' in data:
            verification.verification_date = parse_date(data['verification_date'])
        if 'verification_status' in data:
            verification.verification_status = data['verification_status']
        if 'verifier_id' in data:
            verification.verifier_id = data['verifier_id']
        if 'verification_notes' in data:
            verification.verification_notes = data['verification_notes']
        if 'documents_checked' in data:
            verification.documents_checked = data['documents_checked']
        if 'field_visit_conducted' in data:
            verification.field_visit_conducted = data['field_visit_conducted']
        if 'field_visit_notes' in data:
            verification.field_visit_notes = data['field_visit_notes']
        if 'next_verification_date' in data:
            verification.next_verification_date = parse_date(data['next_verification_date']) if data['next_verification_date'] else None
        
        verification.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data verifikasi berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def beneficiary_verification_delete(request, verification_id):
    """Delete beneficiary verification"""
    try:
        verification = get_object_or_404(BeneficiaryVerification, id=verification_id)
        verification.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Data verifikasi berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ STATISTICS AND HELPERS ============

def beneficiaries_statistics(request):
    """Get beneficiaries statistics"""
    try:
        total_beneficiaries = Beneficiary.objects.count()
        active_beneficiaries = Beneficiary.objects.filter(status='aktif').count()
        total_categories = BeneficiaryCategory.objects.filter(is_active=True).count()
        total_aids = Aid.objects.filter(is_active=True).count()
        total_distributed = AidDistribution.objects.filter(status='distributed').aggregate(total=Sum('amount_received'))['total'] or 0
        
        # Status distribution
        status_distribution = list(Beneficiary.objects.values('status').annotate(count=Count('id')))
        
        # Economic status distribution
        economic_status_distribution = list(Beneficiary.objects.values('economic_status').annotate(count=Count('id')))
        
        # Category distribution
        category_distribution = list(
            BeneficiaryCategory.objects.annotate(
                beneficiaries_count=Count('beneficiary')
            ).values('name', 'beneficiaries_count')
        )
        
        return JsonResponse({
            'total_beneficiaries': total_beneficiaries,
            'active_beneficiaries': active_beneficiaries,
            'total_categories': total_categories,
            'total_aids': total_aids,
            'total_distributed': float(total_distributed),
            'status_distribution': status_distribution,
            'economic_status_distribution': economic_status_distribution,
            'category_distribution': category_distribution,
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error loading statistics: {str(e)}'
        }, status=500)

def beneficiary_categories_dropdown(request):
    """Get beneficiary categories for dropdown"""
    try:
        categories = BeneficiaryCategory.objects.filter(is_active=True).values('id', 'name')
        return JsonResponse({
            'categories': list(categories)
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error loading categories: {str(e)}'
        }, status=500)

def aids_dropdown(request):
    """Get aids for dropdown"""
    try:
        aids = Aid.objects.filter(is_active=True).values('id', 'name')
        return JsonResponse({
            'aids': list(aids)
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error loading aids: {str(e)}'
        }, status=500)

def beneficiaries_dropdown(request):
    """Get beneficiaries for dropdown"""
    try:
        beneficiaries = Beneficiary.objects.select_related('person').filter(status='aktif').values(
            'id', 'person__nama', 'person__nik'
        )
        return JsonResponse({
            'beneficiaries': list(beneficiaries)
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error loading beneficiaries: {str(e)}'
        }, status=500)

def residents_dropdown(request):
    """Get residents for dropdown"""
    try:
        residents = Penduduk.objects.values('id', 'nama', 'nik')
        return JsonResponse({
            'residents': list(residents)
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error loading residents: {str(e)}'
        }, status=500)


# ============ DASHBOARD VIEWS ============

def beneficiaries_dashboard(request):
    """Render beneficiaries dashboard"""
    return render(request, 'admin/modules/beneficiaries/index.html')

def taraf_kehidupan_page(request):
    """Render taraf kehidupan page"""
    return render(request, 'admin/modules/beneficiaries/taraf_kehidupan.html')

def data_bantuan_page(request):
    """Render data bantuan page"""
    return render(request, 'admin/modules/beneficiaries/data_bantuan.html')

def create_bantuan_page(request):
    """Render create bantuan page"""
    return render(request, 'admin/modules/beneficiaries/create_bantuan.html')

def edit_bantuan_page(request, bantuan_id):
    """Render edit bantuan page"""
    try:
        bantuan = DataBantuan.objects.get(id=bantuan_id)
        context = {
            'bantuan_id': bantuan_id
        }
        return render(request, 'admin/modules/beneficiaries/edit_bantuan.html', context)
    except DataBantuan.DoesNotExist:
        return redirect('beneficiaries:data_bantuan_page')

def upload_dokumen_page(request):
    """Render upload dokumen page"""
    return render(request, 'admin/modules/beneficiaries/upload_dokumen.html')

def membuat_berita_page(request):
    """Render membuat berita page"""
    return render(request, 'admin/modules/beneficiaries/membuat_berita.html')

def membuat_surat_page(request):
    """Render membuat surat page"""
    return render(request, 'admin/modules/beneficiaries/membuat_surat.html')


# ============ TARAF KEHIDUPAN VIEWS ============

def taraf_kehidupan_list(request):
    """List taraf kehidupan with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    taraf_ekonomi = request.GET.get('taraf_ekonomi', '')
    pendidikan = request.GET.get('pendidikan', '')
    pekerjaan = request.GET.get('pekerjaan', '')
    
    taraf_kehidupan = TarafKehidupan.objects.select_related('person', 'surveyor').all()
    
    # Apply filters
    if search:
        taraf_kehidupan = taraf_kehidupan.filter(
            Q(person__nama__icontains=search) |
            Q(person__nik__icontains=search)
        )
    
    if taraf_ekonomi:
        taraf_kehidupan = taraf_kehidupan.filter(taraf_ekonomi=taraf_ekonomi)
    
    if pendidikan:
        taraf_kehidupan = taraf_kehidupan.filter(pendidikan_terakhir=pendidikan)
    
    if pekerjaan:
        taraf_kehidupan = taraf_kehidupan.filter(pekerjaan=pekerjaan)
    
    taraf_kehidupan = taraf_kehidupan.order_by('-tanggal_survei')
    
    # Pagination
    paginator = Paginator(taraf_kehidupan, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for item in page_obj:
        data.append({
            'id': item.id,
            'person_name': item.person.nama,
            'person_nik': item.person.nik,
            'taraf_ekonomi': item.get_taraf_ekonomi_display(),
            'pendapatan_bulanan': float(item.pendapatan_bulanan) if item.pendapatan_bulanan else 0,
            'pendidikan_terakhir': item.get_pendidikan_terakhir_display(),
            'pekerjaan': item.get_pekerjaan_display(),
            'jumlah_tanggungan': item.jumlah_tanggungan,
            'kondisi_rumah': item.get_kondisi_rumah_display(),
            'tanggal_survei': item.tanggal_survei.strftime('%Y-%m-%d'),
            'surveyor': item.surveyor.username if item.surveyor else None,
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def taraf_kehidupan_create(request):
    """Create new taraf kehidupan"""
    try:
        data = json.loads(request.body)
        
        person = get_object_or_404(Penduduk, id=data['person_id'])
        
        taraf_kehidupan = TarafKehidupan.objects.create(
            person=person,
            taraf_ekonomi=data['taraf_ekonomi'],
            pendapatan_bulanan=Decimal(str(data.get('pendapatan_bulanan', 0))) if data.get('pendapatan_bulanan') else None,
            pendidikan_terakhir=data['pendidikan_terakhir'],
            pekerjaan=data['pekerjaan'],
            jumlah_tanggungan=data.get('jumlah_tanggungan', 0),
            kondisi_rumah=data['kondisi_rumah'],
            luas_rumah=Decimal(str(data.get('luas_rumah', 0))) if data.get('luas_rumah') else None,
            kepemilikan_rumah=data.get('kepemilikan_rumah', 'milik_sendiri'),
            sumber_air=data.get('sumber_air', ''),
            jenis_jamban=data.get('jenis_jamban', ''),
            sumber_penerangan=data.get('sumber_penerangan', ''),
            bahan_bakar_memasak=data.get('bahan_bakar_memasak', ''),
            kepemilikan_aset=data.get('kepemilikan_aset', ''),
            catatan_khusus=data.get('catatan_khusus', ''),
            tanggal_survei=parse_date(data['tanggal_survei']),
            surveyor_id=data.get('surveyor_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data taraf kehidupan berhasil disimpan',
            'data': {
                'id': taraf_kehidupan.id,
                'person_name': taraf_kehidupan.person.nama,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def taraf_kehidupan_detail(request, taraf_id):
    """Get taraf kehidupan details"""
    try:
        taraf = get_object_or_404(TarafKehidupan.objects.select_related('person', 'surveyor'), id=taraf_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': taraf.id,
                'person': {
                    'id': taraf.person.id,
                    'nama': taraf.person.nama,
                    'nik': taraf.person.nik,
                },
                'taraf_ekonomi': taraf.taraf_ekonomi,
                'pendapatan_bulanan': float(taraf.pendapatan_bulanan) if taraf.pendapatan_bulanan else 0,
                'pendidikan_terakhir': taraf.pendidikan_terakhir,
                'pekerjaan': taraf.pekerjaan,
                'jumlah_tanggungan': taraf.jumlah_tanggungan,
                'kondisi_rumah': taraf.kondisi_rumah,
                'luas_rumah': float(taraf.luas_rumah) if taraf.luas_rumah else 0,
                'kepemilikan_rumah': taraf.kepemilikan_rumah,
                'sumber_air': taraf.sumber_air,
                'jenis_jamban': taraf.jenis_jamban,
                'sumber_penerangan': taraf.sumber_penerangan,
                'bahan_bakar_memasak': taraf.bahan_bakar_memasak,
                'kepemilikan_aset': taraf.kepemilikan_aset,
                'catatan_khusus': taraf.catatan_khusus,
                'tanggal_survei': taraf.tanggal_survei.strftime('%Y-%m-%d'),
                'surveyor': taraf.surveyor.username if taraf.surveyor else None,
                'created_at': taraf.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': taraf.updated_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def taraf_kehidupan_update(request, taraf_id):
    """Update taraf kehidupan"""
    try:
        taraf = get_object_or_404(TarafKehidupan, id=taraf_id)
        data = json.loads(request.body)
        
        if 'person_id' in data:
            taraf.person = get_object_or_404(Penduduk, id=data['person_id'])
        if 'taraf_ekonomi' in data:
            taraf.taraf_ekonomi = data['taraf_ekonomi']
        if 'pendapatan_bulanan' in data:
            taraf.pendapatan_bulanan = Decimal(str(data['pendapatan_bulanan'])) if data['pendapatan_bulanan'] else None
        if 'pendidikan_terakhir' in data:
            taraf.pendidikan_terakhir = data['pendidikan_terakhir']
        if 'pekerjaan' in data:
            taraf.pekerjaan = data['pekerjaan']
        if 'jumlah_tanggungan' in data:
            taraf.jumlah_tanggungan = data['jumlah_tanggungan']
        if 'kondisi_rumah' in data:
            taraf.kondisi_rumah = data['kondisi_rumah']
        if 'luas_rumah' in data:
            taraf.luas_rumah = Decimal(str(data['luas_rumah'])) if data['luas_rumah'] else None
        if 'kepemilikan_rumah' in data:
            taraf.kepemilikan_rumah = data['kepemilikan_rumah']
        if 'sumber_air' in data:
            taraf.sumber_air = data['sumber_air']
        if 'jenis_jamban' in data:
            taraf.jenis_jamban = data['jenis_jamban']
        if 'sumber_penerangan' in data:
            taraf.sumber_penerangan = data['sumber_penerangan']
        if 'bahan_bakar_memasak' in data:
            taraf.bahan_bakar_memasak = data['bahan_bakar_memasak']
        if 'kepemilikan_aset' in data:
            taraf.kepemilikan_aset = data['kepemilikan_aset']
        if 'catatan_khusus' in data:
            taraf.catatan_khusus = data['catatan_khusus']
        if 'tanggal_survei' in data:
            taraf.tanggal_survei = parse_date(data['tanggal_survei'])
        if 'surveyor_id' in data:
            taraf.surveyor_id = data['surveyor_id']
        
        taraf.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data taraf kehidupan berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def taraf_kehidupan_delete(request, taraf_id):
    """Delete taraf kehidupan"""
    try:
        taraf = get_object_or_404(TarafKehidupan, id=taraf_id)
        taraf.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Data taraf kehidupan berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)


# ============ DATA BANTUAN VIEWS ============

def data_bantuan_list(request):
    """List data bantuan with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    jenis_bantuan = request.GET.get('jenis_bantuan', '')
    status = request.GET.get('status', '')
    
    data_bantuan = DataBantuan.objects.select_related('person', 'input_by').all()
    
    # Apply filters
    if search:
        data_bantuan = data_bantuan.filter(
            Q(person__nama__icontains=search) |
            Q(person__nik__icontains=search) |
            Q(nama_program__icontains=search)
        )
    
    if jenis_bantuan:
        data_bantuan = data_bantuan.filter(jenis_bantuan=jenis_bantuan)
    
    if status:
        data_bantuan = data_bantuan.filter(status=status)
    
    data_bantuan = data_bantuan.order_by('-tanggal_mulai')
    
    # Pagination
    paginator = Paginator(data_bantuan, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for item in page_obj:
        data.append({
            'id': item.id,
            'person_name': item.person.nama,
            'person_nik': item.person.nik,
            'jenis_bantuan': item.get_jenis_bantuan_display(),
            'nama_program': item.nama_program,
            'nomor_kartu': item.nomor_kartu,
            'nilai_bantuan': float(item.nilai_bantuan) if item.nilai_bantuan else 0,
            'tanggal_mulai': item.tanggal_mulai.strftime('%Y-%m-%d'),
            'tanggal_berakhir': item.tanggal_berakhir.strftime('%Y-%m-%d') if item.tanggal_berakhir else None,
            'status': item.get_status_display(),
            'instansi_pemberi': item.instansi_pemberi,
            'input_by': item.input_by.username if item.input_by else None,
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def data_bantuan_create(request):
    """Create new data bantuan"""
    try:
        data = json.loads(request.body)
        
        person = get_object_or_404(Penduduk, id=data['person_id'])
        
        data_bantuan = DataBantuan.objects.create(
            person=person,
            jenis_bantuan=data['jenis_bantuan'],
            nama_program=data['nama_program'],
            nomor_kartu=data.get('nomor_kartu', ''),
            nilai_bantuan=Decimal(str(data.get('nilai_bantuan', 0))) if data.get('nilai_bantuan') else None,
            periode_bantuan=data.get('periode_bantuan', ''),
            tanggal_mulai=parse_date(data['tanggal_mulai']),
            tanggal_berakhir=parse_date(data['tanggal_berakhir']) if data.get('tanggal_berakhir') else None,
            status=data.get('status', 'aktif'),
            sumber_dana=data.get('sumber_dana', ''),
            instansi_pemberi=data.get('instansi_pemberi', ''),
            syarat_penerima=data.get('syarat_penerima', ''),
            dokumen_pendukung=data.get('dokumen_pendukung', ''),
            catatan=data.get('catatan', ''),
            input_by_id=data.get('input_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data bantuan berhasil disimpan',
            'data': {
                'id': data_bantuan.id,
                'person_name': data_bantuan.person.nama,
                'nama_program': data_bantuan.nama_program,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)


# ============ DOKUMEN GAMPONG VIEWS ============

def dokumen_gampong_list(request):
    """List dokumen gampong with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    kategori = request.GET.get('kategori', '')
    status = request.GET.get('status', '')
    
    dokumen = DokumenGampong.objects.select_related('uploaded_by', 'approved_by').all()
    
    # Apply filters
    if search:
        dokumen = dokumen.filter(
            Q(nama_dokumen__icontains=search) |
            Q(deskripsi__icontains=search) |
            Q(tags__icontains=search)
        )
    
    if kategori:
        dokumen = dokumen.filter(kategori=kategori)
    
    if status:
        dokumen = dokumen.filter(status=status)
    
    dokumen = dokumen.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(dokumen, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for item in page_obj:
        data.append({
            'id': item.id,
            'nama_dokumen': item.nama_dokumen,
            'kategori': item.get_kategori_display(),
            'deskripsi': item.deskripsi,
            'file_dokumen': item.file_dokumen.url if item.file_dokumen else None,
            'ukuran_file': item.get_file_size_display(),
            'tipe_file': item.tipe_file,
            'nomor_dokumen': item.nomor_dokumen,
            'tanggal_dokumen': item.tanggal_dokumen.strftime('%Y-%m-%d'),
            'status': item.get_status_display(),
            'is_public': item.is_public,
            'download_count': item.download_count,
            'uploaded_by': item.uploaded_by.username if item.uploaded_by else None,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })


# ============ BERITA VIEWS ============

def berita_list(request):
    """List berita with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    kategori = request.GET.get('kategori', '')
    status = request.GET.get('status', '')
    
    berita = Berita.objects.select_related('author').all()
    
    # Apply filters
    if search:
        berita = berita.filter(
            Q(title__icontains=search) |
            Q(excerpt__icontains=search) |
            Q(content__icontains=search)
        )
    
    if kategori:
        berita = berita.filter(kategori=kategori)
    
    if status:
        berita = berita.filter(status=status)
    
    berita = berita.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(berita, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for item in page_obj:
        data.append({
            'id': item.id,
            'title': item.title,
            'slug': item.slug,
            'excerpt': item.excerpt,
            'kategori': item.get_kategori_display(),
            'status': item.get_status_display(),
            'featured_image': item.featured_image.url if item.featured_image else None,
            'is_featured': item.is_featured,
            'views_count': item.views_count,
            'published_at': item.published_at.strftime('%Y-%m-%d %H:%M') if item.published_at else None,
            'author': item.author.username if item.author else None,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def berita_create(request):
    """Create new berita"""
    try:
        data = json.loads(request.body)
        
        berita = Berita.objects.create(
            title=data['title'],
            excerpt=data.get('excerpt', ''),
            content=data['content'],
            kategori=data['kategori'],
            status=data.get('status', 'draft'),
            tags=data.get('tags', ''),
            is_featured=data.get('is_featured', False),
            allow_comments=data.get('allow_comments', True),
            published_at=parse_date(data['published_at']) if data.get('published_at') else None,
            author_id=data.get('author_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Berita berhasil dibuat',
            'data': {
                'id': berita.id,
                'title': berita.title,
                'slug': berita.slug,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)


# ============ SURAT VIEWS ============

def surat_list(request):
    """List surat with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    jenis = request.GET.get('jenis', '')
    status = request.GET.get('status', '')
    
    surat = Surat.objects.select_related('template', 'created_by', 'approved_by').all()
    
    # Apply filters
    if search:
        surat = surat.filter(
            Q(nomor_surat__icontains=search) |
            Q(perihal__icontains=search) |
            Q(penerima__icontains=search)
        )
    
    if jenis:
        surat = surat.filter(jenis=jenis)
    
    if status:
        surat = surat.filter(status=status)
    
    surat = surat.order_by('-tanggal_surat')
    
    # Pagination
    paginator = Paginator(surat, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for item in page_obj:
        data.append({
            'id': item.id,
            'nomor_surat': item.nomor_surat,
            'perihal': item.perihal,
            'jenis': item.get_jenis_display(),
            'penerima': item.penerima,
            'tanggal_surat': item.tanggal_surat.strftime('%Y-%m-%d'),
            'status': item.get_status_display(),
            'template_name': item.template.nama if item.template else None,
            'file_pdf': item.file_pdf.url if item.file_pdf else None,
            'created_by': item.created_by.username if item.created_by else None,
            'approved_by': item.approved_by.username if item.approved_by else None,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    
    return JsonResponse({
        'results': data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })

@csrf_exempt
@require_http_methods(["POST"])
def surat_create(request):
    """Create new surat"""
    try:
        data = json.loads(request.body)
        
        template = None
        if data.get('template_id'):
            template = get_object_or_404(LetterTemplate, id=data['template_id'])
        
        surat = Surat.objects.create(
            nomor_surat=data['nomor_surat'],
            perihal=data['perihal'],
            jenis=data['jenis'],
            template=template,
            penerima=data['penerima'],
            alamat_penerima=data.get('alamat_penerima', ''),
            content=data['content'],
            variables_data=data.get('variables_data', {}),
            tanggal_surat=parse_date(data['tanggal_surat']),
            status=data.get('status', 'draft'),
            catatan=data.get('catatan', ''),
            created_by_id=data.get('created_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil dibuat',
            'data': {
                'id': surat.id,
                'nomor_surat': surat.nomor_surat,
                'perihal': surat.perihal,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)


# ============ LETTER TEMPLATE VIEWS ============

def letter_template_list(request):
    """List letter templates"""
    try:
        templates = LetterTemplate.objects.filter(is_active=True).values(
            'id', 'nama', 'deskripsi', 'variables'
        )
        return JsonResponse({
            'templates': list(templates)
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Error loading templates: {str(e)}'
        }, status=500)


# ============ ADDITIONAL CRUD OPERATIONS ============

@csrf_exempt
@require_http_methods(["GET"])
def data_bantuan_detail(request, bantuan_id):
    """Get data bantuan details"""
    try:
        bantuan = get_object_or_404(DataBantuan, id=bantuan_id)
        return JsonResponse({
            'success': True,
            'data': {
                'id': bantuan.id,
                'person_id': bantuan.person.id,
                'person_name': bantuan.person.nama,
                'person_nik': bantuan.person.nik,
                'jenis_bantuan': bantuan.jenis_bantuan,
                'nama_program': bantuan.nama_program,
                'nomor_kartu': bantuan.nomor_kartu,
                'nilai_bantuan': float(bantuan.nilai_bantuan) if bantuan.nilai_bantuan else 0,
                'periode_bantuan': bantuan.periode_bantuan,
                'tanggal_mulai': bantuan.tanggal_mulai.strftime('%Y-%m-%d'),
                'tanggal_berakhir': bantuan.tanggal_berakhir.strftime('%Y-%m-%d') if bantuan.tanggal_berakhir else None,
                'status': bantuan.status,
                'sumber_dana': bantuan.sumber_dana,
                'instansi_pemberi': bantuan.instansi_pemberi,
                'syarat_penerima': bantuan.syarat_penerima,
                'dokumen_pendukung': bantuan.dokumen_pendukung,
                'catatan': bantuan.catatan,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def data_bantuan_update(request, bantuan_id):
    """Update data bantuan"""
    try:
        bantuan = get_object_or_404(DataBantuan, id=bantuan_id)
        data = json.loads(request.body)
        
        if 'person_id' in data:
            bantuan.person = get_object_or_404(Penduduk, id=data['person_id'])
        
        bantuan.jenis_bantuan = data.get('jenis_bantuan', bantuan.jenis_bantuan)
        bantuan.nama_program = data.get('nama_program', bantuan.nama_program)
        bantuan.nomor_kartu = data.get('nomor_kartu', bantuan.nomor_kartu)
        
        if 'nilai_bantuan' in data:
            bantuan.nilai_bantuan = Decimal(str(data['nilai_bantuan'])) if data['nilai_bantuan'] else None
        
        bantuan.periode_bantuan = data.get('periode_bantuan', bantuan.periode_bantuan)
        
        if 'tanggal_mulai' in data:
            bantuan.tanggal_mulai = parse_date(data['tanggal_mulai'])
        
        if 'tanggal_berakhir' in data and data['tanggal_berakhir']:
            bantuan.tanggal_berakhir = parse_date(data['tanggal_berakhir'])
        
        bantuan.status = data.get('status', bantuan.status)
        bantuan.sumber_dana = data.get('sumber_dana', bantuan.sumber_dana)
        bantuan.instansi_pemberi = data.get('instansi_pemberi', bantuan.instansi_pemberi)
        bantuan.syarat_penerima = data.get('syarat_penerima', bantuan.syarat_penerima)
        bantuan.dokumen_pendukung = data.get('dokumen_pendukung', bantuan.dokumen_pendukung)
        bantuan.catatan = data.get('catatan', bantuan.catatan)
        
        bantuan.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data bantuan berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def data_bantuan_delete(request, bantuan_id):
    """Delete data bantuan"""
    try:
        bantuan = get_object_or_404(DataBantuan, id=bantuan_id)
        bantuan.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Data bantuan berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def dokumen_gampong_create(request):
    """Create new dokumen gampong"""
    try:
        data = json.loads(request.body)
        
        dokumen = DokumenGampong.objects.create(
            nama_dokumen=data['nama_dokumen'],
            kategori=data['kategori'],
            deskripsi=data.get('deskripsi', ''),
            nomor_dokumen=data.get('nomor_dokumen', ''),
            tanggal_dokumen=parse_date(data['tanggal_dokumen']),
            tags=data.get('tags', ''),
            is_public=data.get('is_public', False),
            uploaded_by_id=data.get('uploaded_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Dokumen berhasil dibuat',
            'data': {
                'id': dokumen.id,
                'nama_dokumen': dokumen.nama_dokumen,
                'kategori': dokumen.get_kategori_display(),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def berita_detail(request, berita_id):
    """Get berita details"""
    try:
        berita = get_object_or_404(Berita, id=berita_id)
        return JsonResponse({
            'success': True,
            'data': {
                'id': berita.id,
                'title': berita.title,
                'slug': berita.slug,
                'excerpt': berita.excerpt,
                'content': berita.content,
                'kategori': berita.kategori,
                'status': berita.status,
                'tags': berita.tags,
                'is_featured': berita.is_featured,
                'allow_comments': berita.allow_comments,
                'views_count': berita.views_count,
                'published_at': berita.published_at.strftime('%Y-%m-%d %H:%M') if berita.published_at else None,
                'featured_image': berita.featured_image.url if berita.featured_image else None,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["GET"])
def surat_detail(request, surat_id):
    """Get surat details"""
    try:
        surat = get_object_or_404(Surat, id=surat_id)
        return JsonResponse({
            'success': True,
            'data': {
                'id': surat.id,
                'nomor_surat': surat.nomor_surat,
                'perihal': surat.perihal,
                'jenis': surat.jenis,
                'template_id': surat.template.id if surat.template else None,
                'template_name': surat.template.nama if surat.template else None,
                'penerima': surat.penerima,
                'alamat_penerima': surat.alamat_penerima,
                'content': surat.content,
                'variables_data': surat.variables_data,
                'tanggal_surat': surat.tanggal_surat.strftime('%Y-%m-%d'),
                'status': surat.status,
                'catatan': surat.catatan,
                'file_pdf': surat.file_pdf.url if surat.file_pdf else None,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)


# ============ MISSING CRUD OPERATIONS ============

@csrf_exempt
@require_http_methods(["PUT"])
def taraf_kehidupan_update(request, taraf_id):
    """Update taraf kehidupan"""
    try:
        taraf = get_object_or_404(TarafKehidupan, id=taraf_id)
        data = json.loads(request.body)
        
        if 'person_id' in data:
            taraf.person = get_object_or_404(Penduduk, id=data['person_id'])
        if 'taraf_ekonomi' in data:
            taraf.taraf_ekonomi = data['taraf_ekonomi']
        if 'pendapatan_bulanan' in data:
            taraf.pendapatan_bulanan = Decimal(str(data['pendapatan_bulanan'])) if data['pendapatan_bulanan'] else None
        if 'pendidikan_terakhir' in data:
            taraf.pendidikan_terakhir = data['pendidikan_terakhir']
        if 'pekerjaan' in data:
            taraf.pekerjaan = data['pekerjaan']
        if 'jumlah_tanggungan' in data:
            taraf.jumlah_tanggungan = data['jumlah_tanggungan']
        if 'kondisi_rumah' in data:
            taraf.kondisi_rumah = data['kondisi_rumah']
        if 'luas_rumah' in data:
            taraf.luas_rumah = Decimal(str(data['luas_rumah'])) if data['luas_rumah'] else None
        if 'kepemilikan_rumah' in data:
            taraf.kepemilikan_rumah = data['kepemilikan_rumah']
        if 'sumber_air' in data:
            taraf.sumber_air = data['sumber_air']
        if 'jenis_jamban' in data:
            taraf.jenis_jamban = data['jenis_jamban']
        if 'sumber_penerangan' in data:
            taraf.sumber_penerangan = data['sumber_penerangan']
        if 'bahan_bakar_memasak' in data:
            taraf.bahan_bakar_memasak = data['bahan_bakar_memasak']
        if 'kepemilikan_aset' in data:
            taraf.kepemilikan_aset = data['kepemilikan_aset']
        if 'catatan_khusus' in data:
            taraf.catatan_khusus = data['catatan_khusus']
        if 'tanggal_survei' in data:
            taraf.tanggal_survei = parse_date(data['tanggal_survei'])
        if 'surveyor_id' in data:
            taraf.surveyor_id = data['surveyor_id']
        
        taraf.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data taraf kehidupan berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def taraf_kehidupan_delete(request, taraf_id):
    """Delete taraf kehidupan"""
    try:
        taraf = get_object_or_404(TarafKehidupan, id=taraf_id)
        taraf.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Data taraf kehidupan berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def dokumen_gampong_detail(request, dokumen_id):
    """Get dokumen gampong details"""
    try:
        dokumen = get_object_or_404(DokumenGampong.objects.select_related('uploaded_by'), id=dokumen_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': dokumen.id,
                'nama_dokumen': dokumen.nama_dokumen,
                'kategori': dokumen.kategori,
                'deskripsi': dokumen.deskripsi,
                'file_dokumen': dokumen.file_dokumen.url if dokumen.file_dokumen else None,
                'ukuran_file': dokumen.get_file_size_display(),
                'tipe_file': dokumen.tipe_file,
                'nomor_dokumen': dokumen.nomor_dokumen,
                'tanggal_dokumen': dokumen.tanggal_dokumen.strftime('%Y-%m-%d'),
                'tags': dokumen.tags,
                'status': dokumen.status,
                'is_public': dokumen.is_public,
                'download_count': dokumen.download_count,
                'uploaded_by': dokumen.uploaded_by.username if dokumen.uploaded_by else None,
                'created_at': dokumen.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': dokumen.updated_at.strftime('%Y-%m-%d %H:%M'),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=404)

@csrf_exempt
@require_http_methods(["PUT"])
def dokumen_gampong_update(request, dokumen_id):
    """Update dokumen gampong"""
    try:
        dokumen = get_object_or_404(DokumenGampong, id=dokumen_id)
        data = json.loads(request.body)
        
        dokumen.nama_dokumen = data.get('nama_dokumen', dokumen.nama_dokumen)
        dokumen.kategori = data.get('kategori', dokumen.kategori)
        dokumen.deskripsi = data.get('deskripsi', dokumen.deskripsi)
        dokumen.nomor_dokumen = data.get('nomor_dokumen', dokumen.nomor_dokumen)
        
        if 'tanggal_dokumen' in data:
            dokumen.tanggal_dokumen = parse_date(data['tanggal_dokumen'])
        
        dokumen.tags = data.get('tags', dokumen.tags)
        dokumen.status = data.get('status', dokumen.status)
        dokumen.is_public = data.get('is_public', dokumen.is_public)
        
        dokumen.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Dokumen berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def dokumen_gampong_delete(request, dokumen_id):
    """Delete dokumen gampong"""
    try:
        dokumen = get_object_or_404(DokumenGampong, id=dokumen_id)
        dokumen.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Dokumen berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def berita_update(request, berita_id):
    """Update berita"""
    try:
        berita = get_object_or_404(Berita, id=berita_id)
        data = json.loads(request.body)
        
        berita.title = data.get('title', berita.title)
        berita.excerpt = data.get('excerpt', berita.excerpt)
        berita.content = data.get('content', berita.content)
        berita.kategori = data.get('kategori', berita.kategori)
        berita.status = data.get('status', berita.status)
        berita.tags = data.get('tags', berita.tags)
        berita.is_featured = data.get('is_featured', berita.is_featured)
        berita.allow_comments = data.get('allow_comments', berita.allow_comments)
        
        if 'published_at' in data and data['published_at']:
            berita.published_at = parse_date(data['published_at'])
        
        # Update slug if title changed
        if 'title' in data:
            berita.slug = slugify(berita.title)
        
        berita.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Berita berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def berita_delete(request, berita_id):
    """Delete berita"""
    try:
        berita = get_object_or_404(Berita, id=berita_id)
        berita.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Berita berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def surat_create(request):
    """Create new surat"""
    try:
        data = json.loads(request.body)
        
        template = None
        if data.get('template_id'):
            template = get_object_or_404(LetterTemplate, id=data['template_id'])
        
        surat = Surat.objects.create(
            nomor_surat=data['nomor_surat'],
            perihal=data['perihal'],
            jenis=data['jenis'],
            template=template,
            penerima=data['penerima'],
            alamat_penerima=data.get('alamat_penerima', ''),
            content=data['content'],
            variables_data=data.get('variables_data', {}),
            tanggal_surat=parse_date(data['tanggal_surat']),
            status=data.get('status', 'draft'),
            catatan=data.get('catatan', ''),
            created_by_id=data.get('created_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil dibuat',
            'data': {
                'id': surat.id,
                'nomor_surat': surat.nomor_surat,
                'perihal': surat.perihal,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["PUT"])
def surat_update(request, surat_id):
    """Update surat"""
    try:
        surat = get_object_or_404(Surat, id=surat_id)
        data = json.loads(request.body)
        
        surat.nomor_surat = data.get('nomor_surat', surat.nomor_surat)
        surat.perihal = data.get('perihal', surat.perihal)
        surat.jenis = data.get('jenis', surat.jenis)
        surat.penerima = data.get('penerima', surat.penerima)
        surat.alamat_penerima = data.get('alamat_penerima', surat.alamat_penerima)
        surat.content = data.get('content', surat.content)
        surat.variables_data = data.get('variables_data', surat.variables_data)
        surat.status = data.get('status', surat.status)
        surat.catatan = data.get('catatan', surat.catatan)
        
        if 'template_id' in data:
            if data['template_id']:
                surat.template = get_object_or_404(LetterTemplate, id=data['template_id'])
            else:
                surat.template = None
        
        if 'tanggal_surat' in data:
            surat.tanggal_surat = parse_date(data['tanggal_surat'])
        
        if 'approved_by_id' in data:
            surat.approved_by_id = data['approved_by_id']
        
        surat.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil diperbarui'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
@require_http_methods(["DELETE"])
def surat_delete(request, surat_id):
    """Delete surat"""
    try:
        surat = get_object_or_404(Surat, id=surat_id)
        surat.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ EXPORT FUNCTIONS ============

def export_taraf_kehidupan_csv(request):
    """Export taraf kehidupan data to CSV"""
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="taraf_kehidupan.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nama', 'NIK', 'Taraf Ekonomi', 'Pendapatan Bulanan', 'Pendidikan Terakhir',
            'Pekerjaan', 'Jumlah Tanggungan', 'Kondisi Rumah', 'Luas Rumah',
            'Kepemilikan Rumah', 'Sumber Air', 'Jenis Jamban', 'Sumber Penerangan',
            'Bahan Bakar Memasak', 'Kepemilikan Aset', 'Tanggal Survei', 'Surveyor'
        ])
        
        taraf_kehidupan = TarafKehidupan.objects.select_related('person', 'surveyor').all()
        
        for item in taraf_kehidupan:
            writer.writerow([
                item.person.nama,
                item.person.nik,
                item.get_taraf_ekonomi_display(),
                item.pendapatan_bulanan or 0,
                item.get_pendidikan_terakhir_display(),
                item.get_pekerjaan_display(),
                item.jumlah_tanggungan,
                item.get_kondisi_rumah_display(),
                item.luas_rumah or 0,
                item.get_kepemilikan_rumah_display(),
                item.sumber_air,
                item.jenis_jamban,
                item.sumber_penerangan,
                item.bahan_bakar_memasak,
                item.kepemilikan_aset,
                item.tanggal_survei.strftime('%Y-%m-%d'),
                item.surveyor.username if item.surveyor else ''
            ])
        
        return response
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error exporting data: {str(e)}'
        }, status=500)

def export_data_bantuan_csv(request):
    """Export data bantuan to CSV"""
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data_bantuan.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nama Penerima', 'NIK', 'Jenis Bantuan', 'Nama Program', 'Nomor Kartu',
            'Nilai Bantuan', 'Periode Bantuan', 'Tanggal Mulai', 'Tanggal Berakhir',
            'Status', 'Sumber Dana', 'Instansi Pemberi'
        ])
        
        data_bantuan = DataBantuan.objects.select_related('penerima').all()
        
        for item in data_bantuan:
            writer.writerow([
                item.penerima.nama,
                item.penerima.nik,
                item.get_jenis_bantuan_display(),
                item.nama_program,
                item.nomor_kartu,
                item.nilai_bantuan or 0,
                item.periode_bantuan,
                item.tanggal_mulai.strftime('%Y-%m-%d'),
                item.tanggal_berakhir.strftime('%Y-%m-%d') if item.tanggal_berakhir else '',
                item.get_status_display(),
                item.sumber_dana,
                item.instansi_pemberi
            ])
        
        return response
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error exporting data: {str(e)}'
        }, status=500)

def export_beneficiaries_csv(request):
    """Export beneficiaries data to CSV"""
    try:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="penerima_bantuan.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Nama', 'NIK', 'Kategori', 'Tanggal Registrasi', 'Status',
            'Status Ekonomi', 'Pendapatan Bulanan', 'Jumlah Anggota Keluarga',
            'Kondisi Rumah', 'Kebutuhan Khusus', 'Tanggal Verifikasi'
        ])
        
        beneficiaries = Beneficiary.objects.select_related('person', 'category').all()
        
        for item in beneficiaries:
            writer.writerow([
                item.person.nama,
                item.person.nik,
                item.category.name,
                item.registration_date.strftime('%Y-%m-%d'),
                item.get_status_display(),
                item.get_economic_status_display(),
                item.monthly_income or 0,
                item.family_members_count,
                item.house_condition,
                item.special_needs,
                item.verification_date.strftime('%Y-%m-%d') if item.verification_date else ''
            ])
        
        return response
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error exporting data: {str(e)}'
        }, status=500)

# ============ STATISTICS AND HELPER FUNCTIONS ============

def dashboard_statistics(request):
    """Get dashboard statistics for beneficiaries module"""
    try:
        # Basic counts
        total_beneficiaries = Beneficiary.objects.count()
        total_taraf_kehidupan = TarafKehidupan.objects.count()
        total_data_bantuan = DataBantuan.objects.count()
        total_dokumen = DokumenGampong.objects.count()
        total_berita = Berita.objects.count()
        total_surat = Surat.objects.count()
        
        # Active counts
        active_bantuan = DataBantuan.objects.filter(status='aktif').count()
        published_berita = Berita.objects.filter(status='published').count()
        approved_surat = Surat.objects.filter(status='approved').count()
        
        # Economic status distribution
        economic_distribution = TarafKehidupan.objects.values('status_ekonomi').annotate(
            count=Count('id')
        ).order_by('status_ekonomi')
        
        # Aid type distribution
        aid_distribution = DataBantuan.objects.values('jenis_bantuan').annotate(
            count=Count('id')
        ).order_by('jenis_bantuan')
        
        return JsonResponse({
            'success': True,
            'data': {
                'totals': {
                    'beneficiaries': total_beneficiaries,
                    'taraf_kehidupan': total_taraf_kehidupan,
                    'data_bantuan': total_data_bantuan,
                    'dokumen': total_dokumen,
                    'berita': total_berita,
                    'surat': total_surat,
                },
                'active_counts': {
                    'active_bantuan': active_bantuan,
                    'published_berita': published_berita,
                    'approved_surat': approved_surat,
                },
                'distributions': {
                    'economic_status': list(economic_distribution),
                    'aid_types': list(aid_distribution),
                }
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
