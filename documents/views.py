from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
import json

from .models import DocumentType, Document, DocumentRequest, DocumentApproval, DocumentTemplate
from references.models import Penduduk


@login_required
def documents_admin(request):
    """Main documents admin page"""
    context = {
        'page_title': 'Dokumen',
        'page_subtitle': 'Kelola dokumen dan template desa'
    }
    return render(request, 'admin/modules/documents.html', context)


# Document Type API Views
@login_required
@require_http_methods(["GET"])
def document_type_list_api(request):
    """API to get list of document types"""
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        queryset = DocumentType.objects.annotate(
            document_count=Count('document'),
            template_count=Count('templates')
        )
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': item.id,
                    'name': item.name,
                    'description': item.description,
                    'processing_time_days': item.processing_time_days,
                    'fee': str(item.fee),
                    'is_active': item.is_active,
                    'document_count': item.document_count,
                    'template_count': item.template_count,
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
def document_type_detail_api(request, pk):
    """API to get document type detail"""
    try:
        document_type = get_object_or_404(DocumentType, pk=pk)
        
        data = {
            'id': document_type.id,
            'name': document_type.name,
            'description': document_type.description,
            'required_fields': document_type.required_fields,
            'processing_time_days': document_type.processing_time_days,
            'fee': str(document_type.fee),
            'is_active': document_type.is_active,
            'created_at': document_type.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': document_type.updated_at.strftime('%d/%m/%Y %H:%M')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def document_type_create_api(request):
    """API to create new document type"""
    try:
        data = json.loads(request.body)
        
        document_type = DocumentType.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            required_fields=data.get('required_fields', {}),
            processing_time_days=data.get('processing_time_days', 3),
            fee=data.get('fee', 0),
            is_active=data.get('is_active', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis dokumen berhasil ditambahkan',
            'data': {
                'id': document_type.id,
                'name': document_type.name
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def document_type_update_api(request, pk):
    """API to update document type"""
    try:
        document_type = get_object_or_404(DocumentType, pk=pk)
        data = json.loads(request.body)
        
        document_type.name = data['name']
        document_type.description = data.get('description', '')
        document_type.required_fields = data.get('required_fields', {})
        document_type.processing_time_days = data.get('processing_time_days', 3)
        document_type.fee = data.get('fee', 0)
        document_type.is_active = data.get('is_active', True)
        document_type.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis dokumen berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def document_type_delete_api(request, pk):
    """API to delete document type"""
    try:
        document_type = get_object_or_404(DocumentType, pk=pk)
        
        # Check if document type has documents
        if document_type.document_set.exists():
            return JsonResponse({
                'error': 'Jenis dokumen tidak dapat dihapus karena masih memiliki dokumen'
            }, status=400)
        
        document_type.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Jenis dokumen berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Document API Views
@login_required
@require_http_methods(["GET"])
def document_list_api(request):
    """API to get list of documents"""
    try:
        search = request.GET.get('search', '')
        document_type_id = request.GET.get('document_type_id', '')
        status = request.GET.get('status', '')
        priority = request.GET.get('priority', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        queryset = Document.objects.select_related('document_type', 'applicant', 'created_by')
        
        if search:
            queryset = queryset.filter(
                Q(document_number__icontains=search) |
                Q(title__icontains=search) |
                Q(applicant__nama__icontains=search) |
                Q(content__icontains=search)
            )
        
        if document_type_id:
            queryset = queryset.filter(document_type_id=document_type_id)
        
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
                    'document_number': item.document_number or 'Draft',
                    'document_type': item.document_type.name,
                    'applicant': item.applicant.nama,
                    'applicant_nik': item.applicant.nik,
                    'title': item.title,
                    'status': item.status,
                    'priority': item.priority,
                    'submission_date': item.submission_date.strftime('%d/%m/%Y %H:%M') if item.submission_date else None,
                    'completion_date': item.completion_date.strftime('%d/%m/%Y %H:%M') if item.completion_date else None,
                    'created_by': item.created_by.get_full_name() if item.created_by else None,
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
def document_detail_api(request, pk):
    """API to get document detail"""
    try:
        document = get_object_or_404(
            Document.objects.select_related('document_type', 'applicant', 'created_by')
            .prefetch_related('approvals'),
            pk=pk
        )
        
        data = {
            'id': document.id,
            'document_number': document.document_number,
            'document_type_id': document.document_type.id,
            'document_type': document.document_type.name,
            'applicant_id': document.applicant.id,
            'applicant': document.applicant.nama,
            'applicant_nik': document.applicant.nik,
            'title': document.title,
            'content': document.content,
            'status': document.status,
            'priority': document.priority,
            'submission_date': document.submission_date.strftime('%Y-%m-%dT%H:%M') if document.submission_date else None,
            'completion_date': document.completion_date.strftime('%Y-%m-%dT%H:%M') if document.completion_date else None,
            'notes': document.notes,
            'file_attachment': document.file_attachment.url if document.file_attachment else None,
            'created_by': document.created_by.get_full_name() if document.created_by else None,
            'approvals': [
                {
                    'id': approval.id,
                    'approver': approval.approver.get_full_name(),
                    'approval_level': approval.approval_level,
                    'status': approval.status,
                    'approval_date': approval.approval_date.strftime('%d/%m/%Y %H:%M') if approval.approval_date else None,
                    'comments': approval.comments,
                    'is_final_approval': approval.is_final_approval
                }
                for approval in document.approvals.all()
            ],
            'created_at': document.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': document.updated_at.strftime('%d/%m/%Y %H:%M')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def document_create_api(request):
    """API to create new document"""
    try:
        data = json.loads(request.body)
        
        document = Document.objects.create(
            document_type_id=data['document_type_id'],
            applicant_id=data['applicant_id'],
            title=data['title'],
            content=data['content'],
            status=data.get('status', 'draft'),
            priority=data.get('priority', 'normal'),
            notes=data.get('notes', ''),
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Dokumen berhasil ditambahkan',
            'data': {
                'id': document.id,
                'title': document.title
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
def document_update_api(request, pk):
    """API to update document"""
    try:
        document = get_object_or_404(Document, pk=pk)
        data = json.loads(request.body)
        
        old_status = document.status
        
        document.document_type_id = data['document_type_id']
        document.applicant_id = data['applicant_id']
        document.title = data['title']
        document.content = data['content']
        document.status = data.get('status', 'draft')
        document.priority = data.get('priority', 'normal')
        document.notes = data.get('notes', '')
        
        # Handle status changes
        if old_status != document.status:
            if document.status == 'submitted':
                document.submission_date = timezone.now()
            elif document.status == 'completed':
                document.completion_date = timezone.now()
        
        document.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Dokumen berhasil diperbarui'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def document_delete_api(request, pk):
    """API to delete document"""
    try:
        document = get_object_or_404(Document, pk=pk)
        document.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Dokumen berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Document Request API Views
@login_required
@require_http_methods(["GET"])
def document_request_list_api(request):
    """API to get list of document requests"""
    try:
        search = request.GET.get('search', '')
        document_type_id = request.GET.get('document_type_id', '')
        status = request.GET.get('status', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        queryset = DocumentRequest.objects.select_related('document_type', 'requester', 'processed_by')
        
        if search:
            queryset = queryset.filter(
                Q(requester__nama__icontains=search) |
                Q(purpose__icontains=search) |
                Q(additional_info__icontains=search)
            )
        
        if document_type_id:
            queryset = queryset.filter(document_type_id=document_type_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': item.id,
                    'document_type': item.document_type.name,
                    'requester': item.requester.nama,
                    'requester_nik': item.requester.nik,
                    'purpose': item.purpose,
                    'status': item.status,
                    'request_date': item.request_date.strftime('%d/%m/%Y %H:%M'),
                    'expected_completion_date': item.expected_completion_date.strftime('%d/%m/%Y') if item.expected_completion_date else None,
                    'processed_by': item.processed_by.get_full_name() if item.processed_by else None,
                    'processed_date': item.processed_date.strftime('%d/%m/%Y %H:%M') if item.processed_date else None
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


# Document Template API Views
@login_required
@require_http_methods(["GET"])
def document_template_list_api(request):
    """API to get list of document templates"""
    try:
        search = request.GET.get('search', '')
        template_type = request.GET.get('template_type', '')
        document_type_id = request.GET.get('document_type_id', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        queryset = DocumentTemplate.objects.select_related('document_type', 'created_by')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(content_template__icontains=search)
            )
        
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
        if document_type_id:
            queryset = queryset.filter(document_type_id=document_type_id)
        
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        data = {
            'results': [
                {
                    'id': item.id,
                    'name': item.name,
                    'template_type': item.template_type,
                    'template_type_display': item.get_template_type_display(),
                    'document_type': item.document_type.name,
                    'is_default': item.is_default,
                    'is_active': item.is_active,
                    'created_by': item.created_by.get_full_name() if item.created_by else None,
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


# Statistics API
@login_required
@require_http_methods(["GET"])
def documents_statistics_api(request):
    """API to get documents statistics"""
    try:
        total_documents = Document.objects.count()
        draft_documents = Document.objects.filter(status='draft').count()
        submitted_documents = Document.objects.filter(status='submitted').count()
        approved_documents = Document.objects.filter(status='approved').count()
        completed_documents = Document.objects.filter(status='completed').count()
        total_document_types = DocumentType.objects.filter(is_active=True).count()
        total_templates = DocumentTemplate.objects.filter(is_active=True).count()
        pending_requests = DocumentRequest.objects.filter(status='pending').count()
        
        # This month statistics
        current_month = timezone.now().month
        current_year = timezone.now().year
        this_month_documents = Document.objects.filter(
            created_at__month=current_month,
            created_at__year=current_year
        ).count()
        
        data = {
            'total_documents': total_documents,
            'draft_documents': draft_documents,
            'submitted_documents': submitted_documents,
            'approved_documents': approved_documents,
            'completed_documents': completed_documents,
            'total_document_types': total_document_types,
            'total_templates': total_templates,
            'pending_requests': pending_requests,
            'this_month_documents': this_month_documents
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Helper APIs for dropdowns
@login_required
@require_http_methods(["GET"])
def document_types_dropdown_api(request):
    """API to get document types for dropdown"""
    try:
        document_types = DocumentType.objects.filter(is_active=True).values('id', 'name')
        return JsonResponse({'results': list(document_types)})
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
def documents_dropdown_api(request):
    """API to get documents for dropdown"""
    try:
        documents = Document.objects.exclude(status='draft').values('id', 'document_number', 'title')
        return JsonResponse({'results': list(documents)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
