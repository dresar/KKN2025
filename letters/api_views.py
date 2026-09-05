from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import LetterType, Letter
import json

@csrf_exempt
@require_http_methods(["GET"])
def api_letter_types(request):
    """API endpoint untuk jenis surat"""
    try:
        letter_types = LetterType.objects.filter(is_active=True)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(letter_types, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for letter_type in page_obj:
            results.append({
                'id': letter_type.id,
                'name': letter_type.name,
                'description': letter_type.description,
                'requirements': letter_type.requirements,
                'processing_time': letter_type.processing_time,
                'fee': float(letter_type.fee) if letter_type.fee else 0,
                'template': letter_type.template,
                'created_at': letter_type.created_at.isoformat()
            })
        
        return JsonResponse({
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_letters_stats(request):
    """API endpoint untuk statistik surat"""
    try:
        stats = {
            'total_letters': Letter.objects.count(),
            'pending_letters': Letter.objects.filter(status='pending').count(),
            'approved_letters': Letter.objects.filter(status='approved').count(),
            'rejected_letters': Letter.objects.filter(status='rejected').count(),
            'completed_letters': Letter.objects.filter(status='completed').count(),
            'letter_types': list(LetterType.objects.filter(is_active=True).annotate(
                letter_count=Count('letter')
            ).values('name', 'letter_count')[:5])
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def api_letters_create(request):
    """API endpoint untuk membuat surat baru"""
    try:
        # Handle form data
        letter_type_id = request.POST.get('letter_type')
        applicant_name = request.POST.get('applicant_name')
        applicant_nik = request.POST.get('applicant_nik')
        applicant_phone = request.POST.get('applicant_phone')
        applicant_email = request.POST.get('applicant_email')
        purpose = request.POST.get('purpose')
        notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not all([letter_type_id, applicant_name, applicant_nik, purpose]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        try:
            letter_type = LetterType.objects.get(id=letter_type_id, is_active=True)
        except LetterType.DoesNotExist:
            return JsonResponse({'error': 'Invalid letter type'}, status=400)
        
        # Create letter
        letter = Letter.objects.create(
            letter_type=letter_type,
            applicant_name=applicant_name,
            applicant_nik=applicant_nik,
            applicant_phone=applicant_phone,
            applicant_email=applicant_email,
            purpose=purpose,
            notes=notes,
            status='pending'
        )
        
        return JsonResponse({
            'message': 'Letter created successfully',
            'letter_id': letter.id,
            'tracking_code': letter.tracking_code
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def api_letters_track(request, tracking_code):
    """API endpoint untuk tracking surat"""
    try:
        letter = Letter.objects.get(tracking_code=tracking_code)
        
        data = {
            'id': letter.id,
            'tracking_code': letter.tracking_code,
            'letter_type': {
                'id': letter.letter_type.id,
                'name': letter.letter_type.name
            },
            'applicant_name': letter.applicant_name,
            'applicant_nik': letter.applicant_nik,
            'status': letter.status,
            'purpose': letter.purpose,
            'notes': letter.notes,
            'admin_notes': letter.admin_notes,
            'created_at': letter.created_at.isoformat(),
            'updated_at': letter.updated_at.isoformat(),
            'processed_at': letter.processed_at.isoformat() if letter.processed_at else None,
            'completed_at': letter.completed_at.isoformat() if letter.completed_at else None
        }
        
        return JsonResponse(data)
    except Letter.DoesNotExist:
        return JsonResponse({'error': 'Letter not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)