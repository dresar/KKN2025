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
    TarafKehidupan, DataBantuan
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
        distributions_count = aid.distributions.count()
        data.append({
            'id': aid.id,
            'name': aid.name,
            'aid_type': aid.get_aid_type_display(),
            'source': aid.get_source_display(),
            'value_per_beneficiary': float(aid.value_per_beneficiary),
            'total_budget': float(aid.total_budget),
            'target_beneficiaries': aid.target_beneficiaries,
            'start_date': aid.start_date.strftime('%Y-%m-%d'),
            'end_date': aid.end_date.strftime('%Y-%m-%d'),
            'is_active': aid.is_active,
            'distributions_count': distributions_count,
            'created_by': aid.created_by.username if aid.created_by else None,
            'created_at': aid.created_at.strftime('%Y-%m-%d %H:%M'),
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
        
        # Get distribution statistics
        distributions = aid.distributions.all()
        total_distributed = distributions.filter(status='distributed').count()
        total_pending = distributions.filter(status='pending').count()
        total_approved = distributions.filter(status='approved').count()
        total_rejected = distributions.filter(status='rejected').count()
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': aid.id,
                'name': aid.name,
                'aid_type': aid.aid_type,
                'aid_type_display': aid.get_aid_type_display(),
                'source': aid.source,
                'source_display': aid.get_source_display(),
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
                'statistics': {
                    'total_distributions': distributions.count(),
                    'total_distributed': total_distributed,
                    'total_pending': total_pending,
                    'total_approved': total_approved,
                    'total_rejected': total_rejected,
                }
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
        
        if 'name' in data:
            aid.name = data['name']
        if 'aid_type' in data:
            aid.aid_type = data['aid_type']
        if 'source' in data:
            aid.source = data['source']
        if 'description' in data:
            aid.description = data['description']
        if 'value_per_beneficiary' in data:
            aid.value_per_beneficiary = Decimal(str(data['value_per_beneficiary']))
        if 'total_budget' in data:
            aid.total_budget = Decimal(str(data['total_budget']))
        if 'target_beneficiaries' in data:
            aid.target_beneficiaries = data['target_beneficiaries']
        if 'start_date' in data:
            aid.start_date = parse_date(data['start_date'])
        if 'end_date' in data:
            aid.end_date = parse_date(data['end_date'])
        if 'requirements' in data:
            aid.requirements = data['requirements']
        if 'is_active' in data:
            aid.is_active = data['is_active']
        
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
    
    distributions = AidDistribution.objects.select_related('aid', 'beneficiary', 'beneficiary__person', 'distributed_by').all()
    
    # Apply filters
    if search:
        distributions = distributions.filter(
            Q(beneficiary__person__nama__icontains=search) |
            Q(beneficiary__person__nik__icontains=search) |
            Q(aid__name__icontains=search)
        )
    
    if aid_id:
        distributions = distributions.filter(aid_id=aid_id)
    
    if status:
        distributions = distributions.filter(status=status)
    
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
            'message': 'Distribusi bantuan berhasil dibuat',
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
        distribution = get_object_or_404(
            AidDistribution.objects.select_related('aid', 'beneficiary', 'beneficiary__person', 'distributed_by'),
            id=distribution_id
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': distribution.id,
                'aid': {
                    'id': distribution.aid.id,
                    'name': distribution.aid.name,
                    'aid_type': distribution.aid.get_aid_type_display(),
                    'value_per_beneficiary': float(distribution.aid.value_per_beneficiary),
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
                'status_display': distribution.get_status_display(),
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
            'message': 'Distribusi bantuan berhasil diperbarui'
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
            'message': 'Distribusi bantuan berhasil dihapus'
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
    
    verifications = BeneficiaryVerification.objects.select_related('beneficiary', 'beneficiary__person', 'verifier').all()
    
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
        
        # Update beneficiary verification date if verified
        if verification.verification_status == 'verified':
            beneficiary.verification_date = verification.verification_date
            beneficiary.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Verifikasi berhasil dibuat',
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
        verification = get_object_or_404(
            BeneficiaryVerification.objects.select_related('beneficiary', 'beneficiary__person', 'verifier'),
            id=verification_id
        )
        
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
                'verification_status_display': verification.get_verification_status_display(),
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
        
        # Update beneficiary verification date if verified
        if verification.verification_status == 'verified':
            verification.beneficiary.verification_date = verification.verification_date
            verification.beneficiary.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Verifikasi berhasil diperbarui'
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
            'message': 'Verifikasi berhasil dihapus'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ TARAF KEHIDUPAN ============

def taraf_kehidupan_list(request):
    """List taraf kehidupan with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    taraf = request.GET.get('taraf', '')
    
    taraf_kehidupan = TarafKehidupan.objects.all()
    
    # Apply filters
    if search:
        taraf_kehidupan = taraf_kehidupan.filter(
            Q(nama_kepala_keluarga__icontains=search) |
            Q(nik__icontains=search) |
            Q(alamat__icontains=search)
        )
    
    if taraf:
        taraf_kehidupan = taraf_kehidupan.filter(taraf=taraf)
    
    taraf_kehidupan = taraf_kehidupan.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(taraf_kehidupan, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for item in page_obj:
        data.append({
            'id': item.id,
            'nama_kepala_keluarga': item.nama_kepala_keluarga,
            'nik': item.nik,
            'alamat': item.alamat,
            'taraf': item.get_taraf_display(),
            'pendidikan': item.get_pendidikan_display(),
            'pekerjaan': item.get_pekerjaan_display(),
            'penghasilan_bulanan': float(item.penghasilan_bulanan) if item.penghasilan_bulanan else 0,
            'jumlah_anggota': item.jumlah_anggota,
            'kondisi_rumah': item.get_kondisi_rumah_display(),
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
def taraf_kehidupan_create(request):
    """Create new taraf kehidupan"""
    try:
        data = json.loads(request.body)
        
        taraf = TarafKehidupan.objects.create(
            nama_kepala_keluarga=data['nama_kepala_keluarga'],
            nik=data['nik'],
            alamat=data.get('alamat', ''),
            taraf=data['taraf'],
            pendidikan=data.get('pendidikan', ''),
            pekerjaan=data.get('pekerjaan', ''),
            penghasilan_bulanan=Decimal(str(data.get('penghasilan_bulanan', 0))),
            jumlah_anggota=data.get('jumlah_anggota', 1),
            kondisi_rumah=data.get('kondisi_rumah', ''),
            kepemilikan_rumah=data.get('kepemilikan_rumah', ''),
            fasilitas_rumah=data.get('fasilitas_rumah', ''),
            aset=data.get('aset', ''),
            catatan=data.get('catatan', ''),
            created_by_id=data.get('created_by_id')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data taraf kehidupan berhasil dibuat',
            'data': {
                'id': taraf.id,
                'nama_kepala_keluarga': taraf.nama_kepala_keluarga,
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
        taraf = get_object_or_404(TarafKehidupan, id=taraf_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': taraf.id,
                'nama_kepala_keluarga': taraf.nama_kepala_keluarga,
                'nik': taraf.nik,
                'alamat': taraf.alamat,
                'taraf': taraf.taraf,
                'taraf_display': taraf.get_taraf_display(),
                'pendidikan': taraf.pendidikan,
                'pendidikan_display': taraf.get_pendidikan_display(),
                'pekerjaan': taraf.pekerjaan,
                'pekerjaan_display': taraf.get_pekerjaan_display(),
                'penghasilan_bulanan': float(taraf.penghasilan_bulanan) if taraf.penghasilan_bulanan else 0,
                'jumlah_anggota': taraf.jumlah_anggota,
                'kondisi_rumah': taraf.kondisi_rumah,
                'kondisi_rumah_display': taraf.get_kondisi_rumah_display(),
                'kepemilikan_rumah': taraf.kepemilikan_rumah,
                'fasilitas_rumah': taraf.fasilitas_rumah,
                'aset': taraf.aset,
                'catatan': taraf.catatan,
                'created_by': taraf.created_by.username if taraf.created_by else None,
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
        
        if 'nama_kepala_keluarga' in data:
            taraf.nama_kepala_keluarga = data['nama_kepala_keluarga']
        if 'nik' in data:
            taraf.nik = data['nik']
        if 'alamat' in data:
            taraf.alamat = data['alamat']
        if 'taraf' in data:
            taraf.taraf = data['taraf']
        if 'pendidikan' in data:
            taraf.pendidikan = data['pendidikan']
        if 'pekerjaan' in data:
            taraf.pekerjaan = data['pekerjaan']
        if 'penghasilan_bulanan' in data:
            taraf.penghasilan_bulanan = Decimal(str(data['penghasilan_bulanan']))
        if 'jumlah_anggota' in data:
            taraf.jumlah_anggota = data['jumlah_anggota']
        if 'kondisi_rumah' in data:
            taraf.kondisi_rumah = data['kondisi_rumah']
        if 'kepemilikan_rumah' in data:
            taraf.kepemilikan_rumah = data['kepemilikan_rumah']
        if 'fasilitas_rumah' in data:
            taraf.fasilitas_rumah = data['fasilitas_rumah']
        if 'aset' in data:
            taraf.aset = data['aset']
        if 'catatan' in data:
            taraf.catatan = data['catatan']
        
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

# ============ DATA BANTUAN ============

def data_bantuan_list(request):
    """List data bantuan with pagination and search"""
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    search = request.GET.get('search', '')
    jenis_bantuan = request.GET.get('jenis_bantuan', '')
    status = request.GET.get('status', '')
    
    data_bantuan = DataBantuan.objects.all()
    
    # Apply filters
    if search:
        data_bantuan = data_bantuan.filter(
            Q(nama_penerima__icontains=search) |
            Q(nik_penerima__icontains=search) |
            Q(deskripsi_bantuan__icontains=search)
        )
    
    if jenis_bantuan:
        data_bantuan = data_bantuan.filter(jenis_bantuan=jenis_bantuan)
    
    if status:
        data_bantuan = data_bantuan.filter(status=status)
    
    data_bantuan = data_bantuan.order_by('-tanggal_pengajuan')
    
    # Pagination
    paginator = Paginator(data_bantuan, per_page)
    page_obj = paginator.get_page(page)
    
    # Prepare data
    data = []
    for bantuan in page_obj:
        data.append({
            'id': bantuan.id,
            'nama_penerima': bantuan.person.name,
            'nik_penerima': bantuan.person.nik,
            'jenis_bantuan': bantuan.get_jenis_bantuan_display(),
            'nama_program': bantuan.nama_program,
            'nilai_bantuan': float(bantuan.nilai_bantuan) if bantuan.nilai_bantuan else None,
            'tanggal_mulai': bantuan.tanggal_mulai.strftime('%Y-%m-%d'),
            'tanggal_berakhir': bantuan.tanggal_berakhir.strftime('%Y-%m-%d') if bantuan.tanggal_berakhir else None,
            'status': bantuan.get_status_display(),
            'created_at': bantuan.created_at.strftime('%Y-%m-%d %H:%M'),
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
        
        # Cari penduduk berdasarkan NIK
        try:
            person = Penduduk.objects.get(nik=data['nik_penerima'])
        except Penduduk.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': f'Penduduk dengan NIK {data["nik_penerima"]} tidak ditemukan'
            }, status=404)
        
        # Buat objek DataBantuan dengan model yang benar
        bantuan = DataBantuan.objects.create(
            person=person,
            jenis_bantuan=data['jenis_bantuan'],
            nama_program=data['nama_program'],
            nomor_kartu=data.get('nomor_kartu', ''),
            nilai_bantuan=Decimal(str(data['nilai_bantuan'])) if data.get('nilai_bantuan') else None,
            periode_bantuan=data.get('periode_bantuan', ''),
            tanggal_mulai=parse_date(data['tanggal_mulai']),
            tanggal_berakhir=parse_date(data['tanggal_berakhir']) if data.get('tanggal_berakhir') else None,
            status=data.get('status', 'aktif'),
            sumber_dana=data.get('sumber_dana', ''),
            instansi_pemberi=data.get('instansi_pemberi', ''),
            syarat_penerima=data.get('syarat_penerima', ''),
            dokumen_pendukung=data.get('dokumen_pendukung', ''),
            catatan=data.get('catatan', ''),
            input_by_id=request.user.id if request.user.is_authenticated else None
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Data bantuan berhasil dibuat',
            'data': {
                'id': bantuan.id,
                'nama_penerima': bantuan.person.name,
                'nik_penerima': bantuan.person.nik
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def data_bantuan_detail(request, bantuan_id):
    """Get data bantuan details"""
    try:
        bantuan = get_object_or_404(DataBantuan, id=bantuan_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': bantuan.id,
                'nama_penerima': bantuan.person.name,
                'nik_penerima': bantuan.person.nik,
                'alamat_penerima': bantuan.person.full_address,
                'jenis_bantuan': bantuan.jenis_bantuan,
                'jenis_bantuan_display': bantuan.get_jenis_bantuan_display(),
                'nama_program': bantuan.nama_program,
                'nomor_kartu': bantuan.nomor_kartu,
                'nilai_bantuan': float(bantuan.nilai_bantuan) if bantuan.nilai_bantuan else None,
                'periode_bantuan': bantuan.periode_bantuan,
                'tanggal_mulai': bantuan.tanggal_mulai.strftime('%Y-%m-%d'),
                'tanggal_berakhir': bantuan.tanggal_berakhir.strftime('%Y-%m-%d') if bantuan.tanggal_berakhir else None,
                'status': bantuan.status,
                'status_display': bantuan.get_status_display(),
                'sumber_dana': bantuan.sumber_dana,
                'instansi_pemberi': bantuan.instansi_pemberi,
                'syarat_penerima': bantuan.syarat_penerima,
                'dokumen_pendukung': bantuan.dokumen_pendukung,
                'catatan': bantuan.catatan,
                'input_by': bantuan.input_by.username if bantuan.input_by else None,
                'created_at': bantuan.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': bantuan.updated_at.strftime('%Y-%m-%d %H:%M'),
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
        
        # Jika NIK berubah, perlu update person
        if 'nik_penerima' in data and data['nik_penerima'] != bantuan.person.nik:
            try:
                person = Penduduk.objects.get(nik=data['nik_penerima'])
                bantuan.person = person
            except Penduduk.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': f'Penduduk dengan NIK {data["nik_penerima"]} tidak ditemukan'
                }, status=404)
        
        # Update field-field sesuai model DataBantuan
        if 'jenis_bantuan' in data:
            bantuan.jenis_bantuan = data['jenis_bantuan']
        if 'nama_program' in data:
            bantuan.nama_program = data['nama_program']
        if 'nomor_kartu' in data:
            bantuan.nomor_kartu = data['nomor_kartu']
        if 'nilai_bantuan' in data:
            bantuan.nilai_bantuan = Decimal(str(data['nilai_bantuan'])) if data['nilai_bantuan'] else None
        if 'periode_bantuan' in data:
            bantuan.periode_bantuan = data['periode_bantuan']
        if 'tanggal_mulai' in data:
            bantuan.tanggal_mulai = parse_date(data['tanggal_mulai'])
        if 'tanggal_berakhir' in data:
            bantuan.tanggal_berakhir = parse_date(data['tanggal_berakhir']) if data['tanggal_berakhir'] else None
        if 'status' in data:
            bantuan.status = data['status']
        if 'sumber_dana' in data:
            bantuan.sumber_dana = data['sumber_dana']
        if 'instansi_pemberi' in data:
            bantuan.instansi_pemberi = data['instansi_pemberi']
        if 'syarat_penerima' in data:
            bantuan.syarat_penerima = data['syarat_penerima']
        if 'dokumen_pendukung' in data:
            bantuan.dokumen_pendukung = data['dokumen_pendukung']
        if 'catatan' in data:
            bantuan.catatan = data['catatan']
        
        bantuan.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Data bantuan berhasil diperbarui',
            'data': {
                'id': bantuan.id,
                'nama_penerima': bantuan.person.name,
                'nik_penerima': bantuan.person.nik
            }
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

# ============ STATISTICS ============

def beneficiary_statistics(request):
    """Get beneficiary statistics"""
    try:
        # Total beneficiaries
        total_beneficiaries = Beneficiary.objects.count()
        
        # Beneficiaries by category
        categories = BeneficiaryCategory.objects.all()
        categories_data = []
        for category in categories:
            count = Beneficiary.objects.filter(category=category).count()
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'count': count
            })
        
        # Beneficiaries by status
        active_count = Beneficiary.objects.filter(status='aktif').count()
        inactive_count = Beneficiary.objects.filter(status='tidak_aktif').count()
        pending_count = Beneficiary.objects.filter(status='menunggu').count()
        
        # Beneficiaries by economic status
        economic_status_data = {
            'sangat_miskin': Beneficiary.objects.filter(economic_status='sangat_miskin').count(),
            'miskin': Beneficiary.objects.filter(economic_status='miskin').count(),
            'rentan_miskin': Beneficiary.objects.filter(economic_status='rentan_miskin').count(),
            'menengah': Beneficiary.objects.filter(economic_status='menengah').count(),
            'mampu': Beneficiary.objects.filter(economic_status='mampu').count(),
        }
        
        # Recent registrations
        recent_registrations = Beneficiary.objects.select_related('person', 'category').order_by('-created_at')[:5]
        recent_data = []
        for beneficiary in recent_registrations:
            recent_data.append({
                'id': beneficiary.id,
                'person_name': beneficiary.person.name,
                'category_name': beneficiary.category.name,
                'registration_date': beneficiary.registration_date.strftime('%Y-%m-%d'),
                'created_at': beneficiary.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_beneficiaries': total_beneficiaries,
                'by_category': categories_data,
                'by_status': {
                    'active': active_count,
                    'inactive': inactive_count,
                    'pending': pending_count,
                },
                'by_economic_status': economic_status_data,
                'recent_registrations': recent_data,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

@csrf_exempt
def beneficiary_stats_by_category(request):
    """Get beneficiary statistics by category for charts"""
    try:
        # Get categories with beneficiary counts
        categories = BeneficiaryCategory.objects.filter(is_active=True)
        result = []
        
        for category in categories:
            count = Beneficiary.objects.filter(category=category).count()
            if count > 0:  # Only include categories with beneficiaries
                result.append({
                    'id': category.id,
                    'name': category.name,
                    'count': count
                })
        
        # Sort by count (descending)
        result = sorted(result, key=lambda x: x['count'], reverse=True)
        
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@csrf_exempt
def beneficiary_stats_by_economic_status(request):
    """Get beneficiary statistics by economic status for charts"""
    try:
        # Count beneficiaries by economic status
        economic_statuses = [
            {'economic_status': 'sangat_miskin', 'count': Beneficiary.objects.filter(economic_status='sangat_miskin').count()},
            {'economic_status': 'miskin', 'count': Beneficiary.objects.filter(economic_status='miskin').count()},
            {'economic_status': 'rentan_miskin', 'count': Beneficiary.objects.filter(economic_status='rentan_miskin').count()},
            {'economic_status': 'menengah', 'count': Beneficiary.objects.filter(economic_status='menengah').count()},
            {'economic_status': 'mampu', 'count': Beneficiary.objects.filter(economic_status='mampu').count()},
        ]
        
        # Filter out statuses with zero count
        economic_statuses = [status for status in economic_statuses if status['count'] > 0]
        
        return JsonResponse(economic_statuses, safe=False)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def aid_statistics(request):
    """Get aid statistics"""
    try:
        # Total aids
        total_aids = Aid.objects.count()
        active_aids = Aid.objects.filter(is_active=True).count()
        
        # Aids by type
        aid_types = {
            'uang': Aid.objects.filter(aid_type='uang').count(),
            'barang': Aid.objects.filter(aid_type='barang').count(),
            'jasa': Aid.objects.filter(aid_type='jasa').count(),
            'lainnya': Aid.objects.filter(aid_type='lainnya').count(),
        }
        
        # Aids by source
        aid_sources = {
            'pemerintah': Aid.objects.filter(source='pemerintah').count(),
            'desa': Aid.objects.filter(source='desa').count(),
            'swasta': Aid.objects.filter(source='swasta').count(),
            'individu': Aid.objects.filter(source='individu').count(),
            'lainnya': Aid.objects.filter(source='lainnya').count(),
        }
        
        # Total budget
        total_budget = Aid.objects.aggregate(Sum('total_budget'))['total_budget__sum'] or 0
        
        # Distribution statistics
        total_distributions = AidDistribution.objects.count()
        distributed_count = AidDistribution.objects.filter(status='distributed').count()
        pending_count = AidDistribution.objects.filter(status='pending').count()
        approved_count = AidDistribution.objects.filter(status='approved').count()
        rejected_count = AidDistribution.objects.filter(status='rejected').count()
        
        # Recent aids
        recent_aids = Aid.objects.order_by('-created_at')[:5]
        recent_data = []
        for aid in recent_aids:
            recent_data.append({
                'id': aid.id,
                'name': aid.name,
                'aid_type': aid.get_aid_type_display(),
                'source': aid.get_source_display(),
                'total_budget': float(aid.total_budget),
                'created_at': aid.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_aids': total_aids,
                'active_aids': active_aids,
                'by_type': aid_types,
                'by_source': aid_sources,
                'total_budget': float(total_budget),
                'distribution': {
                    'total': total_distributions,
                    'distributed': distributed_count,
                    'pending': pending_count,
                    'approved': approved_count,
                    'rejected': rejected_count,
                },
                'recent_aids': recent_data,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def verification_statistics(request):
    """Get verification statistics"""
    try:
        # Total verifications
        total_verifications = BeneficiaryVerification.objects.count()
        
        # Verifications by status
        verification_status = {
            'verified': BeneficiaryVerification.objects.filter(verification_status='verified').count(),
            'rejected': BeneficiaryVerification.objects.filter(verification_status='rejected').count(),
            'pending': BeneficiaryVerification.objects.filter(verification_status='pending').count(),
            'needs_review': BeneficiaryVerification.objects.filter(verification_status='needs_review').count(),
        }
        
        # Field visits
        field_visits_conducted = BeneficiaryVerification.objects.filter(field_visit_conducted=True).count()
        
        # Recent verifications
        recent_verifications = BeneficiaryVerification.objects.select_related('beneficiary', 'beneficiary__person').order_by('-verification_date')[:5]
        recent_data = []
        for verification in recent_verifications:
            recent_data.append({
                'id': verification.id,
                'beneficiary_name': verification.beneficiary.person.nama,
                'verification_date': verification.verification_date.strftime('%Y-%m-%d'),
                'verification_status': verification.get_verification_status_display(),
                'field_visit_conducted': verification.field_visit_conducted,
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_verifications': total_verifications,
                'by_status': verification_status,
                'field_visits_conducted': field_visits_conducted,
                'recent_verifications': recent_data,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def taraf_kehidupan_statistics(request):
    """Get taraf kehidupan statistics"""
    try:
        # Total records
        total_records = TarafKehidupan.objects.count()
        
        # By taraf
        taraf_data = {
            'sangat_miskin': TarafKehidupan.objects.filter(taraf='sangat_miskin').count(),
            'miskin': TarafKehidupan.objects.filter(taraf='miskin').count(),
            'rentan_miskin': TarafKehidupan.objects.filter(taraf='rentan_miskin').count(),
            'menengah': TarafKehidupan.objects.filter(taraf='menengah').count(),
            'mampu': TarafKehidupan.objects.filter(taraf='mampu').count(),
        }
        
        # By pendidikan
        pendidikan_data = {
            'tidak_sekolah': TarafKehidupan.objects.filter(pendidikan='tidak_sekolah').count(),
            'sd': TarafKehidupan.objects.filter(pendidikan='sd').count(),
            'smp': TarafKehidupan.objects.filter(pendidikan='smp').count(),
            'sma': TarafKehidupan.objects.filter(pendidikan='sma').count(),
            'diploma': TarafKehidupan.objects.filter(pendidikan='diploma').count(),
            'sarjana': TarafKehidupan.objects.filter(pendidikan='sarjana').count(),
            'pascasarjana': TarafKehidupan.objects.filter(pendidikan='pascasarjana').count(),
        }
        
        # By pekerjaan
        pekerjaan_data = {
            'tidak_bekerja': TarafKehidupan.objects.filter(pekerjaan='tidak_bekerja').count(),
            'petani': TarafKehidupan.objects.filter(pekerjaan='petani').count(),
            'nelayan': TarafKehidupan.objects.filter(pekerjaan='nelayan').count(),
            'buruh': TarafKehidupan.objects.filter(pekerjaan='buruh').count(),
            'pedagang': TarafKehidupan.objects.filter(pekerjaan='pedagang').count(),
            'wiraswasta': TarafKehidupan.objects.filter(pekerjaan='wiraswasta').count(),
            'pns': TarafKehidupan.objects.filter(pekerjaan='pns').count(),
            'tni_polri': TarafKehidupan.objects.filter(pekerjaan='tni_polri').count(),
            'pensiunan': TarafKehidupan.objects.filter(pekerjaan='pensiunan').count(),
            'lainnya': TarafKehidupan.objects.filter(pekerjaan='lainnya').count(),
        }
        
        # By kondisi rumah
        kondisi_rumah_data = {
            'sangat_baik': TarafKehidupan.objects.filter(kondisi_rumah='sangat_baik').count(),
            'baik': TarafKehidupan.objects.filter(kondisi_rumah='baik').count(),
            'cukup': TarafKehidupan.objects.filter(kondisi_rumah='cukup').count(),
            'kurang': TarafKehidupan.objects.filter(kondisi_rumah='kurang').count(),
            'sangat_kurang': TarafKehidupan.objects.filter(kondisi_rumah='sangat_kurang').count(),
        }
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_records': total_records,
                'by_taraf': taraf_data,
                'by_pendidikan': pendidikan_data,
                'by_pekerjaan': pekerjaan_data,
                'by_kondisi_rumah': kondisi_rumah_data,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

# ============ DROPDOWNS ============

def beneficiary_categories_dropdown(request):
    """Get beneficiary categories for dropdown"""
    try:
        categories = BeneficiaryCategory.objects.filter(is_active=True).order_by('name')
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def beneficiaries_dropdown(request):
    """Get beneficiaries for dropdown"""
    try:
        beneficiaries = Beneficiary.objects.select_related('person').filter(status='aktif').order_by('person__nama')
        data = []
        for beneficiary in beneficiaries:
            data.append({
                'id': beneficiary.id,
                'name': beneficiary.person.nama,
                'nik': beneficiary.person.nik,
                'category': beneficiary.category.name,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def aids_dropdown(request):
    """Get aids for dropdown"""
    try:
        aids = Aid.objects.filter(is_active=True).order_by('name')
        data = []
        for aid in aids:
            data.append({
                'id': aid.id,
                'name': aid.name,
                'aid_type': aid.get_aid_type_display(),
                'value_per_beneficiary': float(aid.value_per_beneficiary),
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)

def penduduk_dropdown(request):
    """Get penduduk for dropdown"""
    try:
        search = request.GET.get('search', '')
        penduduk = Penduduk.objects.all().order_by('name')
        
        if search:
            penduduk = penduduk.filter(
                Q(name__icontains=search) |
                Q(nik__icontains=search)
            )
        
        # Limit to 50 results
        penduduk = penduduk[:50]
        
        data = []
        for person in penduduk:
            data.append({
                'id': person.id,
                'nama': person.name,
                'nik': person.nik,
                'tempat_lahir': person.birth_place,
                'tanggal_lahir': person.birth_date.strftime('%Y-%m-%d'),
                'jenis_kelamin': person.gender,
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=400)