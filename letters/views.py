from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import (
    LetterType, Letter, LetterRecipient, LetterAttachment, LetterTracking,
    APIKeySettings, LetterSettings, LetterTemplate, LetterAIValidation,
    LetterDigitalSignature
)
from references.models import Penduduk
from .forms import LetterForm
from .services import (
    GeminiAIService, LetterValidationService, 
    LetterNumberingService, LetterExportService
)
from .utils import (
    generate_qr_code, create_letterhead_image,
    calculate_reading_time, extract_text_statistics,
    generate_letter_hash, validate_file_upload
)
import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# Dashboard Views
@login_required
def letters_admin(request):
    """Main letters admin page"""
    context = {
        'page_title': 'Surat Menyurat',
        'page_subtitle': 'Kelola surat dan administrasi desa'
    }
    return render(request, 'admin/modules/letters.html', context)

@login_required
def letter_dashboard(request):
    """Dashboard dengan statistik dan overview letters"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Statistics
    total_letters = Letter.objects.count()
    pending_letters = Letter.objects.filter(status='pending').count()
    approved_letters = Letter.objects.filter(status='approved').count()
    recent_letters = Letter.objects.filter(created_at__date__gte=week_ago).count()
    
    # AI Validation Stats
    ai_validated = LetterAIValidation.objects.filter(status='valid').count()
    ai_pending = LetterAIValidation.objects.filter(status='pending').count()
    
    # Digital Signature Stats
    signed_letters = Letter.objects.filter(is_digitally_signed=True).count()
    pending_signatures = Letter.objects.filter(
        requires_digital_signature=True,
        is_digitally_signed=False
    ).count()
    
    # Recent activity
    recent_activity = LetterTracking.objects.select_related(
        'letter', 'performed_by'
    ).order_by('-performed_at')[:10]
    
    # Chart data - Letters by type
    letters_by_type = LetterType.objects.annotate(
        letter_count=Count('letter')
    ).values('name', 'letter_count')
    
    # Chart data - Letters by status
    letters_by_status = Letter.objects.values('status').annotate(
        count=Count('id')
    )
    
    context = {
        'total_letters': total_letters,
        'pending_letters': pending_letters,
        'approved_letters': approved_letters,
        'recent_letters': recent_letters,
        'ai_validated': ai_validated,
        'ai_pending': ai_pending,
        'signed_letters': signed_letters,
        'pending_signatures': pending_signatures,
        'recent_activity': recent_activity,
        'letters_by_type': list(letters_by_type),
        'letters_by_status': list(letters_by_status),
    }
    
    return render(request, 'admin/modules/letters/dashboard.html', context)

@login_required
def letter_list(request):
    """List semua letters dengan filter dan search"""
    letters = Letter.objects.select_related(
        'letter_type', 'applicant', 'approved_by', 'created_by'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        letters = letters.filter(
            Q(subject__icontains=search_query) |
            Q(letter_number__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(applicant__nama__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        letters = letters.filter(status=status_filter)
    
    # Filter by letter type
    type_filter = request.GET.get('type')
    if type_filter:
        letters = letters.filter(letter_type_id=type_filter)
    
    # Pagination
    paginator = Paginator(letters, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'letter_types': LetterType.objects.all(),
        'search_query': search_query,
        'status_filter': status_filter,
        'type_filter': type_filter,
    }
    
    return render(request, 'admin/modules/letters/list.html', context)

@login_required
def letter_detail(request, letter_id):
    """Detail letter dengan tracking history"""
    letter = get_object_or_404(Letter.objects.select_related(
        'letter_type', 'applicant', 'approved_by', 'created_by'
    ).prefetch_related(
        'recipients', 'attachments', 'tracking_history'
    ), id=letter_id)
    
    tracking_history = letter.tracking_history.select_related(
        'performed_by'
    ).order_by('-performed_at')
    
    context = {
        'letter': letter,
        'tracking_history': tracking_history,
    }
    
    return render(request, 'admin/modules/letters/detail.html', context)

@login_required
def letter_create(request):
    """Create new letter"""
    if request.method == 'POST':
        form = LetterForm(request.POST, request.FILES)
        if form.is_valid():
            letter = form.save(commit=False)
            letter.created_by = request.user
            letter.save()
            
            # Create tracking entry
            LetterTracking.objects.create(
                letter=letter,
                action='created',
                description='Surat dibuat',
                performed_by=request.user
            )
            
            messages.success(request, 'Surat berhasil dibuat!')
            return redirect('letters:detail', letter_id=letter.id)
    else:
        form = LetterForm()
    
    context = {
        'form': form,
        'letter_types': LetterType.objects.all(),
    }
    
    return render(request, 'admin/modules/letters/create.html', context)

@login_required
def letter_edit(request, letter_id):
    """Edit letter"""
    letter = get_object_or_404(Letter, id=letter_id)
    
    if request.method == 'POST':
        form = LetterForm(request.POST, request.FILES, instance=letter)
        if form.is_valid():
            old_status = letter.status
            letter = form.save()
            
            # Create tracking entry if status changed
            if old_status != letter.status:
                LetterTracking.objects.create(
                    letter=letter,
                    action=letter.status,
                    description=f'Status diubah dari {old_status} ke {letter.status}',
                    performed_by=request.user
                )
            
            messages.success(request, 'Surat berhasil diperbarui!')
            return redirect('letters:detail', letter_id=letter.id)
    else:
        form = LetterForm(instance=letter)
    
    context = {
        'form': form,
        'letter': letter,
        'letter_types': LetterType.objects.all(),
    }
    
    return render(request, 'admin/modules/letters/edit.html', context)

@login_required
@require_http_methods(["DELETE"])
def letter_delete(request, letter_id):
    """Delete letter"""
    letter = get_object_or_404(Letter, id=letter_id)
    
    # Create tracking entry before deletion
    LetterTracking.objects.create(
        letter=letter,
        action='deleted',
        description='Surat dihapus',
        performed_by=request.user
    )
    
    letter.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Surat berhasil dihapus!'
    })

# Export Views
@login_required
def letter_export_pdf(request, letter_id):
    """Export letter to PDF"""
    letter = get_object_or_404(Letter, id=letter_id)
    
    try:
        export_service = LetterExportService()
        pdf_buffer = export_service.export_to_pdf(letter)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{letter.letter_number or "surat"}.pdf"'
        
        # Add tracking entry
        LetterTracking.objects.create(
            letter=letter,
            action='exported_pdf',
            description='Surat diekspor ke PDF',
            performed_by=request.user
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('letters:detail', letter_id=letter.id)

@login_required
def letter_export_docx(request, letter_id):
    """Export letter to DOCX"""
    letter = get_object_or_404(Letter, id=letter_id)
    
    try:
        export_service = LetterExportService()
        docx_buffer = export_service.export_to_docx(letter)
        
        response = HttpResponse(
            docx_buffer.getvalue(), 
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{letter.letter_number or "surat"}.docx"'
        
        # Add tracking entry
        LetterTracking.objects.create(
            letter=letter,
            action='exported_docx',
            description='Surat diekspor ke DOCX',
            performed_by=request.user
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error exporting DOCX: {e}")
        messages.error(request, f'Error: {str(e)}')
        return redirect('letters:detail', letter_id=letter.id)

# Settings Views
@login_required
def letter_settings(request):
    """Letter settings configuration"""
    context = {}
    return render(request, 'admin/modules/letters/settings.html', context)


# Letter Type API Views
@login_required
@require_http_methods(["GET"])
def letter_type_list_api(request):
    """API to get list of letter types"""
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        queryset = LetterType.objects.annotate(
            letter_count=Count('letter')
        )
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': item.id,
                    'name': item.name,
                    'code': item.code,
                    'description': item.description,
                    'processing_time_days': item.processing_time_days,
                    'fee_amount': str(item.fee_amount),
                    'is_active': item.is_active,
                    'letter_count': item.letter_count,
                    'created_at': item.created_at.strftime('%d/%m/%Y %H:%M')
                }
                for item in page_obj
            ],
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letter_type_detail_api(request, pk):
    """API to get letter type detail"""
    try:
        letter_type = get_object_or_404(LetterType, pk=pk)
        
        data = {
            'id': letter_type.id,
            'name': letter_type.name,
            'code': letter_type.code,
            'description': letter_type.description,
            'required_documents': letter_type.required_documents,
            'processing_time_days': letter_type.processing_time_days,
            'fee_amount': str(letter_type.fee_amount),
            'is_active': letter_type.is_active,
            'template_file': letter_type.template_file.url if letter_type.template_file else None,
            'created_at': letter_type.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': letter_type.updated_at.strftime('%d/%m/%Y %H:%M')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_type_create_api(request):
    """API to create new letter type"""
    try:
        data = json.loads(request.body)
        
        letter_type = LetterType.objects.create(
            name=data['name'],
            code=data['code'],
            description=data.get('description', ''),
            required_documents=data.get('required_documents', ''),
            processing_time_days=data.get('processing_time_days', 3),
            fee_amount=data.get('fee_amount', 0),
            is_active=data.get('is_active', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis surat berhasil ditambahkan',
            'data': {
                'id': letter_type.id,
                'name': letter_type.name
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def letter_type_update_api(request, pk):
    """API to update letter type"""
    try:
        letter_type = get_object_or_404(LetterType, pk=pk)
        data = json.loads(request.body)
        
        letter_type.name = data['name']
        letter_type.code = data['code']
        letter_type.description = data.get('description', '')
        letter_type.required_documents = data.get('required_documents', '')
        letter_type.processing_time_days = data.get('processing_time_days', 3)
        letter_type.fee_amount = data.get('fee_amount', 0)
        letter_type.is_active = data.get('is_active', True)
        letter_type.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis surat berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def letter_type_delete_api(request, pk):
    """API to delete letter type"""
    try:
        letter_type = get_object_or_404(LetterType, pk=pk)
        letter_type.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis surat berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Letter API Views
@login_required
@require_http_methods(["GET"])
def letter_list_api(request):
    """API to get list of letters"""
    try:
        search = request.GET.get('search', '')
        status_filter = request.GET.get('status', '')
        type_filter = request.GET.get('type', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        queryset = Letter.objects.select_related(
            'letter_type', 'applicant', 'approved_by', 'created_by'
        ).order_by('-created_at')
        
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) |
                Q(letter_number__icontains=search) |
                Q(content__icontains=search)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        if type_filter:
            queryset = queryset.filter(letter_type_id=type_filter)
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': item.id,
                    'subject': item.subject,
                    'letter_number': item.letter_number,
                    'status': item.status,
                    'letter_type': item.letter_type.name if item.letter_type else None,
                    'applicant': item.applicant.nama if item.applicant else None,
                    'created_at': item.created_at.strftime('%d/%m/%Y %H:%M'),
                    'is_digitally_signed': item.is_digitally_signed
                }
                for item in page_obj
            ],
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_create_api(request):
    """API to create new letter"""
    try:
        data = json.loads(request.body)
        
        letter = Letter.objects.create(
            subject=data['subject'],
            content=data['content'],
            letter_type_id=data.get('letter_type_id'),
            applicant_id=data.get('applicant_id'),
            created_by=request.user,
            status='draft'
        )
        
        # Auto-generate letter number if needed
        if not letter.letter_number:
            numbering_service = LetterNumberingService()
            letter.letter_number = numbering_service.generate_number(letter)
            letter.save()
        
        # Create tracking entry
        LetterTracking.objects.create(
            letter=letter,
            action='created',
            description='Surat dibuat melalui API',
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil dibuat',
            'data': {
                'id': letter.id,
                'letter_number': letter.letter_number
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letter_detail_api(request, pk):
    """API to get letter detail"""
    try:
        letter = get_object_or_404(Letter.objects.select_related(
            'letter_type', 'applicant', 'approved_by', 'created_by'
        ), pk=pk)
        
        data = {
            'id': letter.id,
            'subject': letter.subject,
            'content': letter.content,
            'letter_number': letter.letter_number,
            'status': letter.status,
            'letter_type': {
                'id': letter.letter_type.id,
                'name': letter.letter_type.name
            } if letter.letter_type else None,
            'applicant': {
                'id': letter.applicant.id,
                'nama': letter.applicant.nama
            } if letter.applicant else None,
            'is_digitally_signed': letter.is_digitally_signed,
            'requires_digital_signature': letter.requires_digital_signature,
            'created_at': letter.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': letter.updated_at.strftime('%d/%m/%Y %H:%M')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def letter_update_api(request, pk):
    """API to update letter"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        data = json.loads(request.body)
        
        old_status = letter.status
        
        letter.subject = data.get('subject', letter.subject)
        letter.content = data.get('content', letter.content)
        letter.status = data.get('status', letter.status)
        letter.save()
        
        # Create tracking entry if status changed
        if old_status != letter.status:
            LetterTracking.objects.create(
                letter=letter,
                action=letter.status,
                description=f'Status diubah dari {old_status} ke {letter.status} melalui API',
                performed_by=request.user
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def letter_delete_api(request, pk):
    """API to delete letter"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        
        # Create tracking entry before deletion
        LetterTracking.objects.create(
            letter=letter,
            action='deleted',
            description='Surat dihapus melalui API',
            performed_by=request.user
        )
        
        letter.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Letter Recipient API Views
@login_required
@require_http_methods(["GET"])
def letter_recipient_list_api(request, letter_id):
    """API to get letter recipients"""
    try:
        letter = get_object_or_404(Letter, id=letter_id)
        recipients = letter.recipients.all()
        
        data = {
            'results': [
                {
                    'id': recipient.id,
                    'name': recipient.name,
                    'position': recipient.position,
                    'organization': recipient.organization,
                    'email': recipient.email,
                    'phone': recipient.phone,
                    'address': recipient.address
                }
                for recipient in recipients
            ]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_recipient_create_api(request, letter_id):
    """API to create letter recipient"""
    try:
        letter = get_object_or_404(Letter, id=letter_id)
        data = json.loads(request.body)
        
        recipient = LetterRecipient.objects.create(
            letter=letter,
            name=data['name'],
            position=data.get('position', ''),
            organization=data.get('organization', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Penerima surat berhasil ditambahkan',
            'data': {'id': recipient.id}
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letter_recipient_detail_api(request, pk):
    """API to get recipient detail"""
    try:
        recipient = get_object_or_404(LetterRecipient, pk=pk)
        
        data = {
            'id': recipient.id,
            'name': recipient.name,
            'position': recipient.position,
            'organization': recipient.organization,
            'email': recipient.email,
            'phone': recipient.phone,
            'address': recipient.address
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def letter_recipient_update_api(request, pk):
    """API to update recipient"""
    try:
        recipient = get_object_or_404(LetterRecipient, pk=pk)
        data = json.loads(request.body)
        
        recipient.name = data.get('name', recipient.name)
        recipient.position = data.get('position', recipient.position)
        recipient.organization = data.get('organization', recipient.organization)
        recipient.email = data.get('email', recipient.email)
        recipient.phone = data.get('phone', recipient.phone)
        recipient.address = data.get('address', recipient.address)
        recipient.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Penerima surat berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def letter_recipient_delete_api(request, pk):
    """API to delete recipient"""
    try:
        recipient = get_object_or_404(LetterRecipient, pk=pk)
        recipient.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Penerima surat berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Letter Attachment API Views
@login_required
@require_http_methods(["GET"])
def letter_attachment_list_api(request, letter_id):
    """API to get letter attachments"""
    try:
        letter = get_object_or_404(Letter, id=letter_id)
        attachments = letter.attachments.all()
        
        data = {
            'results': [
                {
                    'id': attachment.id,
                    'name': attachment.name,
                    'file_url': attachment.file.url if attachment.file else None,
                    'file_size': attachment.file.size if attachment.file else 0,
                    'uploaded_at': attachment.uploaded_at.strftime('%d/%m/%Y %H:%M')
                }
                for attachment in attachments
            ]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_attachment_create_api(request, letter_id):
    """API to create letter attachment"""
    try:
        letter = get_object_or_404(Letter, id=letter_id)
        
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'File tidak ditemukan'}, status=400)
        
        file = request.FILES['file']
        name = request.POST.get('name', file.name)
        
        # Validate file
        if not validate_file_upload(file):
            return JsonResponse({'error': 'File tidak valid'}, status=400)
        
        attachment = LetterAttachment.objects.create(
            letter=letter,
            name=name,
            file=file,
            uploaded_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Lampiran berhasil ditambahkan',
            'data': {'id': attachment.id}
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letter_attachment_detail_api(request, pk):
    """API to get attachment detail"""
    try:
        attachment = get_object_or_404(LetterAttachment, pk=pk)
        
        data = {
            'id': attachment.id,
            'name': attachment.name,
            'file_url': attachment.file.url if attachment.file else None,
            'file_size': attachment.file.size if attachment.file else 0,
            'uploaded_at': attachment.uploaded_at.strftime('%d/%m/%Y %H:%M')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def letter_attachment_update_api(request, pk):
    """API to update attachment"""
    try:
        attachment = get_object_or_404(LetterAttachment, pk=pk)
        data = json.loads(request.body)
        
        attachment.name = data.get('name', attachment.name)
        attachment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Lampiran berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def letter_attachment_delete_api(request, pk):
    """API to delete attachment"""
    try:
        attachment = get_object_or_404(LetterAttachment, pk=pk)
        attachment.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Lampiran berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Letter Tracking API Views
@login_required
@require_http_methods(["GET"])
def letter_tracking_list_api(request, letter_id):
    """API to get letter tracking history"""
    try:
        letter = get_object_or_404(Letter, id=letter_id)
        tracking = letter.tracking_history.select_related('performed_by').order_by('-performed_at')
        
        data = {
            'results': [
                {
                    'id': track.id,
                    'action': track.action,
                    'description': track.description,
                    'performed_by': track.performed_by.get_full_name() if track.performed_by else None,
                    'performed_at': track.performed_at.strftime('%d/%m/%Y %H:%M')
                }
                for track in tracking
            ]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_tracking_create_api(request, letter_id):
    """API to create tracking entry"""
    try:
        letter = get_object_or_404(Letter, id=letter_id)
        data = json.loads(request.body)
        
        tracking = LetterTracking.objects.create(
            letter=letter,
            action=data['action'],
            description=data.get('description', ''),
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Tracking berhasil ditambahkan',
            'data': {'id': tracking.id}
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letter_tracking_detail_api(request, pk):
    """API to get tracking detail"""
    try:
        tracking = get_object_or_404(LetterTracking, pk=pk)
        
        data = {
            'id': tracking.id,
            'action': tracking.action,
            'description': tracking.description,
            'performed_by': tracking.performed_by.get_full_name() if tracking.performed_by else None,
            'performed_at': tracking.performed_at.strftime('%d/%m/%Y %H:%M')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def letter_tracking_update_api(request, pk):
    """API to update tracking"""
    try:
        tracking = get_object_or_404(LetterTracking, pk=pk)
        data = json.loads(request.body)
        
        tracking.action = data.get('action', tracking.action)
        tracking.description = data.get('description', tracking.description)
        tracking.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Tracking berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def letter_tracking_delete_api(request, pk):
    """API to delete tracking"""
    try:
        tracking = get_object_or_404(LetterTracking, pk=pk)
        tracking.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Tracking berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        if letter_type.letter_set.exists():
            return JsonResponse({
                'error': 'Jenis surat tidak dapat dihapus karena masih memiliki surat'
            }, status=400)
        
        letter_type.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis surat berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Letter API Views
@login_required
@require_http_methods(["GET"])
def letter_list_api(request):
    """API to get list of letters"""
    try:
        search = request.GET.get('search', '')
        letter_type_id = request.GET.get('letter_type_id', '')
        status = request.GET.get('status', '')
        priority = request.GET.get('priority', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        queryset = Letter.objects.select_related('letter_type', 'applicant', 'approved_by', 'created_by')
        
        if search:
            queryset = queryset.filter(
                Q(letter_number__icontains=search) |
                Q(subject__icontains=search) |
                Q(applicant__nama__icontains=search) |
                Q(content__icontains=search)
            )
        
        if letter_type_id:
            queryset = queryset.filter(letter_type_id=letter_type_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': item.id,
                    'letter_number': item.letter_number or 'Draft',
                    'letter_type': item.letter_type.name,
                    'letter_type_code': item.letter_type.code,
                    'applicant': item.applicant.nama,
                    'applicant_nik': item.applicant.nik,
                    'subject': item.subject,
                    'status': item.status,
                    'priority': item.priority,
                    'submission_date': item.submission_date.strftime('%d/%m/%Y %H:%M') if item.submission_date else None,
                    'approval_date': item.approval_date.strftime('%d/%m/%Y %H:%M') if item.approval_date else None,
                    'completion_date': item.completion_date.strftime('%d/%m/%Y %H:%M') if item.completion_date else None,
                    'approved_by': item.approved_by.get_full_name() if item.approved_by else None,
                    'created_by': item.created_by.get_full_name() or item.created_by.username,
                    'created_at': item.created_at.strftime('%d/%m/%Y %H:%M')
                }
                for item in page_obj
            ],
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letter_detail_api(request, pk):
    """API to get letter detail"""
    try:
        letter = get_object_or_404(
            Letter.objects.select_related('letter_type', 'applicant', 'approved_by', 'created_by')
            .prefetch_related('recipients', 'attachments', 'tracking_history'),
            pk=pk
        )
        
        data = {
            'id': letter.id,
            'letter_number': letter.letter_number,
            'letter_type_id': letter.letter_type.id,
            'letter_type': letter.letter_type.name,
            'applicant_id': letter.applicant.id,
            'applicant': letter.applicant.nama,
            'applicant_nik': letter.applicant.nik,
            'subject': letter.subject,
            'content': letter.content,
            'purpose': letter.purpose,
            'status': letter.status,
            'priority': letter.priority,
            'submission_date': letter.submission_date.strftime('%Y-%m-%dT%H:%M') if letter.submission_date else None,
            'approval_date': letter.approval_date.strftime('%Y-%m-%dT%H:%M') if letter.approval_date else None,
            'completion_date': letter.completion_date.strftime('%Y-%m-%dT%H:%M') if letter.completion_date else None,
            'approved_by': letter.approved_by.get_full_name() if letter.approved_by else None,
            'rejection_reason': letter.rejection_reason,
            'notes': letter.notes,
            'created_by': letter.created_by.get_full_name() or letter.created_by.username,
            'recipients': [
                {
                    'id': recipient.id,
                    'name': recipient.name,
                    'organization': recipient.organization,
                    'address': recipient.address,
                    'is_primary': recipient.is_primary
                }
                for recipient in letter.recipients.all()
            ],
            'attachments': [
                {
                    'id': attachment.id,
                    'title': attachment.title,
                    'attachment_type': attachment.attachment_type,
                    'file_url': attachment.file.url if attachment.file else None,
                    'is_required': attachment.is_required
                }
                for attachment in letter.attachments.all()
            ],
            'created_at': letter.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': letter.updated_at.strftime('%d/%m/%Y %H:%M')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_create_api(request):
    """API to create new letter"""
    try:
        data = json.loads(request.body)
        
        letter = Letter.objects.create(
            letter_type_id=data['letter_type_id'],
            applicant_id=data['applicant_id'],
            subject=data['subject'],
            content=data['content'],
            purpose=data['purpose'],
            status=data.get('status', 'draft'),
            priority=data.get('priority', 'normal'),
            notes=data.get('notes', ''),
            created_by=request.user
        )
        
        # Add tracking entry
        LetterTracking.objects.create(
            letter=letter,
            action='created',
            description=f'Surat {letter.subject} dibuat',
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil ditambahkan',
            'data': {
                'id': letter.id,
                'subject': letter.subject
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def letter_update_api(request, pk):
    """API to update letter"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        data = json.loads(request.body)
        
        old_status = letter.status
        
        letter.letter_type_id = data['letter_type_id']
        letter.applicant_id = data['applicant_id']
        letter.subject = data['subject']
        letter.content = data['content']
        letter.purpose = data['purpose']
        letter.status = data.get('status', 'draft')
        letter.priority = data.get('priority', 'normal')
        letter.notes = data.get('notes', '')
        
        # Handle status changes
        if old_status != letter.status:
            if letter.status == 'submitted':
                letter.submission_date = timezone.now()
            elif letter.status == 'approved':
                letter.approval_date = timezone.now()
                letter.approved_by = request.user
            elif letter.status == 'completed':
                letter.completion_date = timezone.now()
            
            # Add tracking entry for status change
            LetterTracking.objects.create(
                letter=letter,
                action=letter.status,
                description=f'Status surat diubah menjadi {letter.get_status_display()}',
                performed_by=request.user
            )
        
        letter.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def letter_delete_api(request, pk):
    """API to delete letter"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        letter.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Letter Tracking API Views
@login_required
@require_http_methods(["GET"])
def letter_tracking_api(request, letter_id):
    """API to get letter tracking history"""
    try:
        letter = get_object_or_404(Letter, pk=letter_id)
        tracking_history = letter.tracking_history.select_related('performed_by').all()
        
        data = {
            'results': [
                {
                    'id': item.id,
                    'action': item.action,
                    'action_display': item.get_action_display(),
                    'description': item.description,
                    'performed_by': item.performed_by.get_full_name() or item.performed_by.username,
                    'performed_at': item.performed_at.strftime('%d/%m/%Y %H:%M'),
                    'location': item.location,
                    'notes': item.notes
                }
                for item in tracking_history
            ]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Statistics API
@login_required
@require_http_methods(["GET"])
def letters_statistics_api(request):
    """API to get letters statistics"""
    try:
        total_letters = Letter.objects.count()
        draft_letters = Letter.objects.filter(status='draft').count()
        submitted_letters = Letter.objects.filter(status='submitted').count()
        approved_letters = Letter.objects.filter(status='approved').count()
        completed_letters = Letter.objects.filter(status='completed').count()
        rejected_letters = Letter.objects.filter(status='rejected').count()
        total_letter_types = LetterType.objects.filter(is_active=True).count()
        
        # This month statistics
        current_month = timezone.now().month
        current_year = timezone.now().year
        this_month_letters = Letter.objects.filter(
            created_at__month=current_month,
            created_at__year=current_year
        ).count()
        
        data = {
            'total_letters': total_letters,
            'draft_letters': draft_letters,
            'submitted_letters': submitted_letters,
            'approved_letters': approved_letters,
            'completed_letters': completed_letters,
            'rejected_letters': rejected_letters,
            'total_letter_types': total_letter_types,
            'this_month_letters': this_month_letters
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Helper APIs for dropdowns
@login_required
@require_http_methods(["GET"])
def letter_types_dropdown_api(request):
    """API to get letter types for dropdown"""
    try:
        letter_types = LetterType.objects.filter(is_active=True).values('id', 'name', 'code')
        return JsonResponse({'results': list(letter_types)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def residents_dropdown_api(request):
    """API to get residents for dropdown"""
    try:
        search = request.GET.get('search', '')
        queryset = Penduduk.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(nama__icontains=search) |
                Q(nik__icontains=search)
            )
        
        residents = queryset.values('id', 'nama', 'nik')[:20]  # Limit to 20 results
        return JsonResponse({'results': list(residents)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letters_dropdown_api(request):
    """API to get letters for dropdown"""
    try:
        letters = Letter.objects.exclude(status='draft').values('id', 'letter_number', 'subject')
        return JsonResponse({'results': list(letters)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# AI Integration APIs
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_ai_validate_api(request, pk):
    """API to validate letter with AI"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        
        # Initialize AI service
        ai_service = GeminiAIService()
        validation_result = ai_service.validate_letter_content(letter.content)
        
        # Save validation result
        ai_validation, created = LetterAIValidation.objects.get_or_create(
            letter=letter,
            defaults={
                'validation_details': validation_result,
                'status': 'valid' if validation_result.get('is_valid') else 'invalid',
                'suggestions': validation_result.get('suggestions', []),
                'confidence_score': validation_result.get('confidence', 0.0)
            }
        )
        
        if not created:
            ai_validation.validation_details = validation_result
            ai_validation.status = 'valid' if validation_result.get('is_valid') else 'invalid'
            ai_validation.suggestions = validation_result.get('suggestions', [])
            ai_validation.confidence_score = validation_result.get('confidence', 0.0)
            ai_validation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Validasi AI berhasil',
            'data': {
                'is_valid': validation_result.get('is_valid'),
                'confidence': validation_result.get('confidence'),
                'suggestions': validation_result.get('suggestions', [])
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_ai_generate_api(request):
    """API to generate letter content with AI"""
    try:
        data = json.loads(request.body)
        
        ai_service = GeminiAIService()
        generated_content = ai_service.generate_letter_content(
            letter_type=data.get('letter_type'),
            purpose=data.get('purpose'),
            recipient=data.get('recipient'),
            additional_info=data.get('additional_info', {})
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'content': generated_content.get('content'),
                'suggestions': generated_content.get('suggestions', []),
                'template_used': generated_content.get('template_used')
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_ai_summarize_api(request, pk):
    """API to generate letter summary with AI"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        
        ai_service = GeminiAIService()
        summary = ai_service.summarize_letter(letter.content)
        
        return JsonResponse({
            'success': True,
            'data': {
                'summary': summary.get('summary'),
                'key_points': summary.get('key_points', []),
                'word_count': len(letter.content.split()),
                'reading_time': calculate_reading_time(letter.content)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_ai_improve_api(request, pk):
    """API to get AI suggestions for letter improvement"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        
        ai_service = GeminiAIService()
        improvements = ai_service.suggest_improvements(letter.content)
        
        return JsonResponse({
            'success': True,
            'data': {
                'improved_content': improvements.get('improved_content'),
                'suggestions': improvements.get('suggestions', []),
                'changes': improvements.get('changes', [])
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Digital Signature APIs
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_digital_sign_api(request, pk):
    """API to digitally sign letter"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        data = json.loads(request.body)
        
        # Create digital signature
        signature = LetterDigitalSignature.objects.create(
            letter=letter,
            signer=request.user,
            signature_data=data.get('signature_data'),
            signature_hash=generate_letter_hash(letter.content),
            signature_method=data.get('signature_method', 'digital'),
            certificate_info=data.get('certificate_info', {})
        )
        
        # Update letter status
        letter.is_digitally_signed = True
        letter.save()
        
        # Add tracking entry
        LetterTracking.objects.create(
            letter=letter,
            action='signed',
            description=f'Surat ditandatangani secara digital oleh {request.user.get_full_name()}',
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Surat berhasil ditandatangani secara digital',
            'data': {
                'signature_id': signature.id,
                'signature_timestamp': signature.signature_timestamp.isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def letter_signature_verify_api(request, pk):
    """API to verify digital signature"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        signatures = letter.digital_signatures.all()
        
        verification_results = []
        for signature in signatures:
            # Verify signature integrity
            current_hash = generate_letter_hash(letter.content)
            is_valid = current_hash == signature.signature_hash
            
            verification_results.append({
                'signature_id': signature.id,
                'signer': signature.signer.get_full_name(),
                'timestamp': signature.signature_timestamp.isoformat(),
                'is_valid': is_valid,
                'signature_method': signature.signature_method
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'signatures': verification_results,
                'overall_valid': all(sig['is_valid'] for sig in verification_results)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Template Management APIs
@login_required
@require_http_methods(["GET"])
def letter_templates_api(request):
    """API to get letter templates"""
    try:
        templates = LetterTemplate.objects.filter(is_active=True)
        
        data = {
            'results': [
                {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'content': template.content,
                    'variables': template.template_variables,
                    'category': template.category
                }
                for template in templates
            ]
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def letter_apply_template_api(request, pk):
    """API to apply template to letter"""
    try:
        letter = get_object_or_404(Letter, pk=pk)
        data = json.loads(request.body)
        
        template = get_object_or_404(LetterTemplate, pk=data['template_id'])
        variables = data.get('variables', {})
        
        # Apply template with variable substitution
        content = template.content
        for key, value in variables.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        letter.content = content
        letter.save()
        
        # Add tracking entry
        LetterTracking.objects.create(
            letter=letter,
            action='template_applied',
            description=f'Template "{template.name}" diterapkan',
            performed_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Template berhasil diterapkan',
            'data': {
                'content': content
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
