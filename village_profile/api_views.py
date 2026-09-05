from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import VillageHistory, VillageHistoryPhoto
import json


@csrf_exempt
@require_http_methods(["GET"])
def api_village_history_list(request):
    """API endpoint untuk daftar sejarah desa"""
    try:
        # Parameter query
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        search = request.GET.get('search', '')
        history_type = request.GET.get('type', '')
        is_featured = request.GET.get('featured', '')
        
        # Base queryset
        queryset = VillageHistory.objects.filter(is_active=True)
        
        # Filter berdasarkan pencarian
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(summary__icontains=search)
            )
        
        # Filter berdasarkan jenis sejarah
        if history_type:
            queryset = queryset.filter(history_type=history_type)
        
        # Filter berdasarkan featured
        if is_featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Ordering
        queryset = queryset.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize data
        results = []
        for history in page_obj:
            # Get photos for this history
            photos = VillageHistoryPhoto.objects.filter(
                history=history, 
                is_active=True
            ).order_by('display_order')
            
            photo_data = []
            for photo in photos:
                photo_data.append({
                    'id': photo.id,
                    'image': photo.image.url if photo.image else None,
                    'caption': photo.caption,
                    'description': photo.description,
                    'photographer': photo.photographer,
                    'photo_date': photo.photo_date.isoformat() if photo.photo_date else None,
                    'location': photo.location,
                    'is_featured': photo.is_featured,
                    'display_order': photo.display_order
                })
            
            results.append({
                'id': history.id,
                'title': history.title,
                'slug': history.slug,
                'summary': history.summary,
                'content': history.content,
                'history_type': history.history_type,
                'history_type_display': history.get_history_type_display(),
                'year_start': history.year_start,
                'year_end': history.year_end,
                'period_start': history.period_start,
                 'period_end': history.period_end,
                'period_display': history.period_display,
                'featured_image': history.featured_image.url if history.featured_image else None,
                'source': history.source,
                'author': history.author,
                'is_featured': history.is_featured,
                'view_count': history.view_count,
                'photo_count': history.photo_count,
                'photos': photo_data,
                'created_at': history.created_at.isoformat(),
                'updated_at': history.updated_at.isoformat()
            })
        
        return JsonResponse({
            'results': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_history_detail(request, history_id):
    """API endpoint untuk detail sejarah desa"""
    try:
        history = get_object_or_404(VillageHistory, id=history_id, is_active=True)
        
        # Increment view count
        history.view_count += 1
        history.save(update_fields=['view_count'])
        
        # Get photos for this history
        photos = VillageHistoryPhoto.objects.filter(
            history=history, 
            is_active=True
        ).order_by('display_order')
        
        photo_data = []
        for photo in photos:
            photo_data.append({
                'id': photo.id,
                'image': photo.image.url if photo.image else None,
                'caption': photo.caption,
                'description': photo.description,
                'photographer': photo.photographer,
                'photo_date': photo.photo_date.isoformat() if photo.photo_date else None,
                'location': photo.location,
                'is_featured': photo.is_featured,
                'display_order': photo.display_order,
                'created_at': photo.created_at.isoformat()
            })
        
        result = {
            'id': history.id,
            'title': history.title,
            'slug': history.slug,
            'summary': history.summary,
            'content': history.content,
            'history_type': history.history_type,
            'history_type_display': history.get_history_type_display(),
            'year_start': history.year_start,
            'year_end': history.year_end,
            'period_start': history.period_start,
             'period_end': history.period_end,
            'period_display': history.period_display,
            'featured_image': history.featured_image.url if history.featured_image else None,
            'source': history.source,
            'author': history.author,
            'is_featured': history.is_featured,
            'view_count': history.view_count,
            'photo_count': history.photo_count,
            'photos': photo_data,
            'created_at': history.created_at.isoformat(),
            'updated_at': history.updated_at.isoformat()
        }
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_history_featured(request):
    """API endpoint untuk sejarah desa yang ditampilkan di beranda"""
    try:
        limit = int(request.GET.get('limit', 5))
        
        histories = VillageHistory.objects.filter(
            is_active=True, 
            is_featured=True
        ).order_by('-created_at')[:limit]
        
        results = []
        for history in histories:
            # Get featured photo
            featured_photo = VillageHistoryPhoto.objects.filter(
                history=history,
                is_active=True,
                is_featured=True
            ).first()
            
            results.append({
                'id': history.id,
                'title': history.title,
                'slug': history.slug,
                'summary': history.summary,
                'history_type': history.history_type,
                'history_type_display': history.get_history_type_display(),
                'year_start': history.year_start,
                'year_end': history.year_end,
                'period_display': history.period_display,
                'featured_image': history.featured_image.url if history.featured_image else None,
                'featured_photo': {
                    'image': featured_photo.image.url if featured_photo and featured_photo.image else None,
                    'caption': featured_photo.caption if featured_photo else None
                } if featured_photo else None,
                'view_count': history.view_count,
                'photo_count': history.photo_count,
                'created_at': history.created_at.isoformat()
            })
        
        return JsonResponse({
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_history_stats(request):
    """API endpoint untuk statistik sejarah desa"""
    try:
        stats = {
            'total_histories': VillageHistory.objects.filter(is_active=True).count(),
            'featured_histories': VillageHistory.objects.filter(is_active=True, is_featured=True).count(),
            'total_photos': VillageHistoryPhoto.objects.filter(is_active=True).count(),
            'histories_by_type': {},
            'recent_histories': VillageHistory.objects.filter(is_active=True).count(),
            'most_viewed': None
        }
        
        # Statistics by history type
        for choice in VillageHistory.HISTORY_TYPE_CHOICES:
            type_code = choice[0]
            type_name = choice[1]
            count = VillageHistory.objects.filter(
                is_active=True, 
                history_type=type_code
            ).count()
            stats['histories_by_type'][type_code] = {
                'name': type_name,
                'count': count
            }
        
        # Most viewed history
        most_viewed = VillageHistory.objects.filter(
            is_active=True
        ).order_by('-view_count').first()
        
        if most_viewed:
            stats['most_viewed'] = {
                'id': most_viewed.id,
                'title': most_viewed.title,
                'slug': most_viewed.slug,
                'view_count': most_viewed.view_count
            }
        
        return JsonResponse(stats)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_history_search(request):
    """API endpoint untuk pencarian sejarah desa"""
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({'error': 'Query parameter is required'}, status=400)
        
        # Search in title, content, and summary
        histories = VillageHistory.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query),
            is_active=True
        ).order_by('-created_at')
        
        results = []
        for history in histories:
            results.append({
                'id': history.id,
                'title': history.title,
                'slug': history.slug,
                'summary': history.summary,
                'history_type': history.history_type,
                'history_type_display': history.get_history_type_display(),
                'featured_image': history.featured_image.url if history.featured_image else None,
                'is_featured': history.is_featured,
                'view_count': history.view_count,
                'created_at': history.created_at.isoformat()
            })
        
        return JsonResponse({
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_village_history_photos(request, history_id):
    """API endpoint untuk foto-foto sejarah desa tertentu"""
    try:
        history = get_object_or_404(VillageHistory, id=history_id, is_active=True)
        
        photos = VillageHistoryPhoto.objects.filter(
            history=history,
            is_active=True
        ).order_by('display_order')
        
        results = []
        for photo in photos:
            results.append({
                'id': photo.id,
                'image': photo.image.url if photo.image else None,
                'caption': photo.caption,
                'description': photo.description,
                'photographer': photo.photographer,
                'photo_date': photo.photo_date.isoformat() if photo.photo_date else None,
                'location': photo.location,
                'is_featured': photo.is_featured,
                'display_order': photo.display_order,
                'created_at': photo.created_at.isoformat()
            })
        
        return JsonResponse({
            'history': {
                'id': history.id,
                'title': history.title,
                'slug': history.slug
            },
            'photos': results,
            'count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Legacy API endpoints for backward compatibility
@csrf_exempt
@require_http_methods(["GET"])
def api_village_profile(request):
    """Legacy API endpoint - redirects to history"""
    return JsonResponse({
        'message': 'This endpoint has been deprecated. Use /api/village-history/ instead.',
        'redirect_to': '/api/village-history/'
    }, status=301)


@csrf_exempt
@require_http_methods(["GET"])
def api_organization_stats(request):
    """Legacy API endpoint - redirects to history stats"""
    return JsonResponse({
        'message': 'This endpoint has been deprecated. Use /api/village-history/stats/ instead.',
        'redirect_to': '/api/village-history/stats/'
    }, status=301)


# CRUD API Endpoints for AJAX Operations
@csrf_exempt
@require_http_methods(["POST"])
def api_village_history_create(request):
    """API endpoint untuk membuat sejarah desa baru via AJAX"""
    try:
        if request.method == 'POST':
            # Get form data
            title = request.POST.get('title')
            summary = request.POST.get('summary', '')
            content = request.POST.get('content')
            history_type = request.POST.get('history_type', 'OTHER')
            period_start = request.POST.get('period_start', '')
            period_end = request.POST.get('period_end', '')
            year_start = request.POST.get('year_start')
            year_end = request.POST.get('year_end')
            source = request.POST.get('source', '')
            author = request.POST.get('author', '')
            is_featured = request.POST.get('is_featured') == 'on'
            featured_image = request.FILES.get('featured_image')
            featured_image_caption = request.POST.get('featured_image_caption', '')
            
            # Validation
            if not title or not content:
                return JsonResponse({
                    'success': False,
                    'error': 'Judul dan konten harus diisi'
                }, status=400)
            
            # Create history object
            history_data = {
                'title': title,
                'summary': summary,
                'content': content,
                'history_type': history_type,
                'period_start': period_start if period_start else None,
                'period_end': period_end if period_end else None,
                'source': source,
                'author': author,
                'is_featured': is_featured,
                'featured_image_caption': featured_image_caption
            }
            
            # Handle year fields
            if year_start:
                try:
                    history_data['year_start'] = int(year_start)
                except ValueError:
                    pass
            
            if year_end:
                try:
                    history_data['year_end'] = int(year_end)
                except ValueError:
                    pass
            
            # Create history
            history = VillageHistory.objects.create(**history_data)
            
            # Handle featured image
            if featured_image:
                history.featured_image = featured_image
                history.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Sejarah berhasil ditambahkan',
                'data': {
                    'id': history.id,
                    'title': history.title,
                    'slug': history.slug
                }
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_village_history_update(request, history_id):
    """API endpoint untuk mengupdate sejarah desa via AJAX"""
    try:
        history = get_object_or_404(VillageHistory, id=history_id)
        
        if request.method == 'POST':
            # Update fields
            history.title = request.POST.get('title', history.title)
            history.summary = request.POST.get('summary', history.summary)
            history.content = request.POST.get('content', history.content)
            history.history_type = request.POST.get('history_type', history.history_type)
            history.period_start = request.POST.get('period_start') or None
            history.period_end = request.POST.get('period_end') or None
            history.source = request.POST.get('source', history.source)
            history.author = request.POST.get('author', history.author)
            history.is_featured = request.POST.get('is_featured') == 'on'
            history.featured_image_caption = request.POST.get('featured_image_caption', history.featured_image_caption)
            
            # Handle year fields
            year_start = request.POST.get('year_start')
            if year_start:
                try:
                    history.year_start = int(year_start)
                except ValueError:
                    pass
            
            year_end = request.POST.get('year_end')
            if year_end:
                try:
                    history.year_end = int(year_end)
                except ValueError:
                    pass
            
            # Handle featured image
            featured_image = request.FILES.get('featured_image')
            if featured_image:
                history.featured_image = featured_image
            
            history.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Sejarah berhasil diperbarui',
                'data': {
                    'id': history.id,
                    'title': history.title,
                    'slug': history.slug
                }
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_village_history_delete(request, history_id):
    """API endpoint untuk menghapus sejarah desa via AJAX"""
    try:
        history = get_object_or_404(VillageHistory, id=history_id)
        
        # Soft delete - set is_active to False
        history.is_active = False
        history.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Sejarah berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_village_history_photo_upload(request, history_id):
    """API endpoint untuk upload foto sejarah via AJAX"""
    try:
        history = get_object_or_404(VillageHistory, id=history_id)
        
        if request.method == 'POST':
            photos = request.FILES.getlist('photos')
            
            if not photos:
                return JsonResponse({
                    'success': False,
                    'error': 'Tidak ada foto yang diupload'
                }, status=400)
            
            uploaded_photos = []
            
            for i, photo in enumerate(photos):
                # Create photo object
                photo_obj = VillageHistoryPhoto.objects.create(
                    history=history,
                    image=photo,
                    caption=request.POST.get(f'caption_{i}', ''),
                    description=request.POST.get(f'description_{i}', ''),
                    photographer=request.POST.get(f'photographer_{i}', ''),
                    location=request.POST.get(f'location_{i}', ''),
                    display_order=i + 1
                )
                
                uploaded_photos.append({
                    'id': photo_obj.id,
                    'image': photo_obj.image.url,
                    'caption': photo_obj.caption
                })
            
            return JsonResponse({
                'success': True,
                'message': f'{len(uploaded_photos)} foto berhasil diupload',
                'photos': uploaded_photos
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def api_village_history_photo_delete(request, photo_id):
    """API endpoint untuk menghapus foto sejarah via AJAX"""
    try:
        photo = get_object_or_404(VillageHistoryPhoto, id=photo_id)
        
        # Soft delete - set is_active to False
        photo.is_active = False
        photo.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Foto berhasil dihapus'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)