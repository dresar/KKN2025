from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count
import json
from datetime import datetime, timedelta

# Import models from other apps
from references.models import Penduduk, Dusun, DisabilitasType, DisabilitasData
from news.models import News, NewsCategory
from village_profile.models import VillageHistory, VillageHistoryPhoto
from core.models import CustomUser, UserProfile, UMKMBusiness, WebsiteSettings
from business.models import Business


def api_stats(request):
    """API untuk statistik umum"""
    try:
        # Statistik penduduk
        total_penduduk = Penduduk.objects.count()
        laki_laki = Penduduk.objects.filter(gender='Laki-laki').count()
        perempuan = Penduduk.objects.filter(gender='Perempuan').count()
        
        # Statistik berita
        total_berita = News.objects.filter(status='published').count()
        berita_bulan_ini = News.objects.filter(
            status='published',
            created_at__month=datetime.now().month,
            created_at__year=datetime.now().year
        ).count()
        
        # Statistik acara (placeholder - no events model)
        total_acara = 0
        acara_mendatang = 0
        
        # Statistik UMKM
        total_umkm = Business.objects.filter(status='active').count()
        
        data = {
            'penduduk': {
                'total': total_penduduk,
                'laki_laki': laki_laki,
                'perempuan': perempuan
            },
            'berita': {
                'total': total_berita,
                'bulan_ini': berita_bulan_ini
            },
            'acara': {
                'total': total_acara,
                'mendatang': acara_mendatang
            },
            'umkm': {
                'total': total_umkm
            }
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_news(request):
    """API untuk berita"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        ordering = request.GET.get('ordering', '-created_at')
        
        news_list = News.objects.filter(status='published').order_by(ordering)
        
        paginator = Paginator(news_list, page_size)
        news_page = paginator.get_page(page)
        
        news_data = []
        for news in news_page:
            news_data.append({
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'excerpt': news.excerpt,
                'image': news.featured_image.url if news.featured_image else None,
                'created_at': news.created_at.isoformat(),
                'category': news.category.name if news.category else None,
                'author': news.author.username if news.author else 'Admin'
            })
        
        return JsonResponse({
            'results': news_data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': news_page.has_next(),
            'has_previous': news_page.has_previous()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_events(request):
    """API untuk acara/kegiatan - placeholder (no events model)"""
    try:
        return JsonResponse({
            'results': [],
            'count': 0,
            'num_pages': 0,
            'current_page': 1
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_event_detail(request, event_id):
    """API untuk detail acara - placeholder (no events model)"""
    try:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_village_profile(request):
    """API untuk profil desa"""
    try:
        profile_type = request.GET.get('type', 'all')
        
        if profile_type == 'peta':
            # Return map data if needed
            return JsonResponse({'message': 'Map data not implemented yet'})
        
        # Get village profile data
        try:
            visi_profile = VillageProfile.objects.filter(profile_type='visi').first()
            misi_profile = VillageProfile.objects.filter(profile_type='misi').first()
            sejarah_profile = VillageProfile.objects.filter(profile_type='sejarah').first()
            geografis_profile = VillageProfile.objects.filter(profile_type='geografis').first()
        except:
            visi_profile = misi_profile = sejarah_profile = geografis_profile = None
        
        data = {
            'visi': visi_profile.content if visi_profile else '',
            'misi': misi_profile.content if misi_profile else '',
            'sejarah': sejarah_profile.content if sejarah_profile else '',
            'geografis': geografis_profile.content if geografis_profile else ''
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_population(request):
    """API untuk data penduduk"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        dusun_nama = request.GET.get('dusun_nama')
        lorong_nama = request.GET.get('lorong_nama')
        
        penduduk_list = Penduduk.objects.all()
        
        if dusun_nama:
            penduduk_list = penduduk_list.filter(dusun__nama__icontains=dusun_nama)
        if lorong_nama:
            penduduk_list = penduduk_list.filter(lorong__nama__icontains=lorong_nama)
        
        paginator = Paginator(penduduk_list, page_size)
        penduduk_page = paginator.get_page(page)
        
        penduduk_data = []
        for penduduk in penduduk_page:
            penduduk_data.append({
                'id': penduduk.id,
                'nama': penduduk.nama,
                'nik': penduduk.nik,
                'jenis_kelamin': penduduk.jenis_kelamin,
                'tanggal_lahir': penduduk.tanggal_lahir.isoformat() if penduduk.tanggal_lahir else None,
                'dusun': penduduk.dusun.nama if penduduk.dusun else None,
                'lorong': penduduk.lorong.nama if penduduk.lorong else None
            })
        
        return JsonResponse({
            'results': penduduk_data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_dusun(request):
    """API untuk data dusun"""
    try:
        dusun_list = Dusun.objects.all()
        dusun_data = []
        for dusun in dusun_list:
            dusun_data.append({
                'id': dusun.id,
                'nama': dusun.nama,
                'kode': dusun.kode if hasattr(dusun, 'kode') else None
            })
        return JsonResponse({'results': dusun_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_contact(request):
    """API untuk kontak"""
    try:
        contact = Contact.objects.first()
        if contact:
            data = {
                'phone': contact.phone,
                'email': contact.email,
                'address': contact.address,
                'website': contact.website if hasattr(contact, 'website') else None
            }
        else:
            data = {
                'phone': '',
                'email': '',
                'address': '',
                'website': ''
            }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_village_history(request):
    """API publik untuk daftar sejarah desa"""
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        history_type = request.GET.get('type')
        featured_only = request.GET.get('featured') == 'true'
        search = request.GET.get('search')
        
        # Filter sejarah yang aktif
        history_list = VillageHistory.objects.filter(is_active=True)
        
        # Filter berdasarkan parameter
        if history_type:
            history_list = history_list.filter(history_type=history_type)
        if featured_only:
            history_list = history_list.filter(is_featured=True)
        if search:
            history_list = history_list.filter(
                Q(title__icontains=search) | 
                Q(summary__icontains=search) |
                Q(content__icontains=search)
            )
        
        # Urutkan berdasarkan featured dan tanggal
        history_list = history_list.order_by('-is_featured', '-created_at')
        
        paginator = Paginator(history_list, page_size)
        history_page = paginator.get_page(page)
        
        history_data = []
        for history in history_page:
            history_data.append({
                'id': history.id,
                'title': history.title,
                'slug': history.slug,
                'summary': history.summary,
                'history_type': history.history_type,
                'history_type_display': history.get_history_type_display(),
                'start_year': history.start_year,
                'end_year': history.end_year,
                'period_string': history.period_string,
                'period_display': history.get_period_display(),
                'featured_image': history.featured_image.url if history.featured_image else None,
                'is_featured': history.is_featured,
                'view_count': history.view_count,
                'photo_count': history.photo_count,
                'created_at': history.created_at.isoformat(),
                'updated_at': history.updated_at.isoformat()
            })
        
        return JsonResponse({
            'results': history_data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_village_history_detail(request, history_id):
    """API publik untuk detail sejarah desa"""
    try:
        history = get_object_or_404(VillageHistory, id=history_id, is_active=True)
        
        # Increment view count
        history.view_count += 1
        history.save(update_fields=['view_count'])
        
        # Get photos
        photos = VillageHistoryPhoto.objects.filter(
            history=history, 
            is_active=True
        ).order_by('display_order', '-is_featured')
        
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
        
        data = {
            'id': history.id,
            'title': history.title,
            'slug': history.slug,
            'summary': history.summary,
            'content': history.content,
            'history_type': history.history_type,
            'history_type_display': history.get_history_type_display(),
            'start_year': history.start_year,
            'end_year': history.end_year,
            'period_string': history.period_string,
            'period_display': history.get_period_display(),
            'featured_image': history.featured_image.url if history.featured_image else None,
            'source': history.source,
            'author': history.author,
            'is_featured': history.is_featured,
            'view_count': history.view_count,
            'photos': photo_data,
            'photo_count': len(photo_data),
            'created_at': history.created_at.isoformat(),
            'updated_at': history.updated_at.isoformat()
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_village_history_featured(request):
    """API publik untuk sejarah desa unggulan"""
    try:
        limit = int(request.GET.get('limit', 5))
        
        featured_history = VillageHistory.objects.filter(
            is_active=True, 
            is_featured=True
        ).order_by('-created_at')[:limit]
        
        history_data = []
        for history in featured_history:
            history_data.append({
                'id': history.id,
                'title': history.title,
                'slug': history.slug,
                'summary': history.summary,
                'history_type': history.history_type,
                'history_type_display': history.get_history_type_display(),
                'period_display': history.get_period_display(),
                'featured_image': history.featured_image.url if history.featured_image else None,
                'view_count': history.view_count,
                'photo_count': history.photo_count,
                'created_at': history.created_at.isoformat()
            })
        
        return JsonResponse({
            'results': history_data,
            'count': len(history_data)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def api_messages(request):
    """API untuk mengirim pesan"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = Message.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                subject=data.get('subject'),
                message=data.get('message')
            )
            return JsonResponse({
                'success': True,
                'message': 'Pesan berhasil dikirim',
                'id': message.id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)