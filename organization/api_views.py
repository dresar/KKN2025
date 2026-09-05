from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import PerangkatDesa, LembagaAdat, PenggerakPKK, Kepemudaan, KarangTaruna
import json
import logging
from .views import handle_api_error

logger = logging.getLogger(__name__)


# ===== PUBLIC API ENDPOINTS FOR WEBSITE =====

@csrf_exempt
@require_http_methods(["GET"])
def api_organization_stats(request):
    """API endpoint untuk statistik organisasi - untuk public website"""
    try:
        stats = {
            'perangkat_desa': PerangkatDesa.objects.filter(status='aktif').count(),
            'lembaga_adat': LembagaAdat.objects.filter(status='aktif').count(),
            'penggerak_pkk': PenggerakPKK.objects.filter(status='aktif').count(),
            'kepemudaan': Kepemudaan.objects.filter(status='aktif').count(),
            'karang_taruna': KarangTaruna.objects.filter(status='aktif').count(),
            'total_organisasi': (
                PerangkatDesa.objects.filter(status='aktif').count() +
                LembagaAdat.objects.filter(status='aktif').count() +
                PenggerakPKK.objects.filter(status='aktif').count() +
                Kepemudaan.objects.filter(status='aktif').count() +
                KarangTaruna.objects.filter(status='aktif').count()
            )
        }
        
        return JsonResponse({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return handle_api_error(e, "retrieving organization stats", logger)


@csrf_exempt
@require_http_methods(["GET"])
def api_perangkat_desa(request):
    """API endpoint untuk data perangkat desa - untuk public website"""
    try:
        search_query = request.GET.get('search', '')
        jabatan_filter = request.GET.get('jabatan', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        perangkat_list = PerangkatDesa.objects.filter(status='aktif').select_related('penduduk')
        
        if search_query:
            perangkat_list = perangkat_list.filter(
                Q(penduduk__name__icontains=search_query) |
                Q(jabatan__icontains=search_query) |
                Q(deskripsi_tugas__icontains=search_query)
            )
        
        if jabatan_filter:
            perangkat_list = perangkat_list.filter(jabatan=jabatan_filter)
        
        # Order by jabatan hierarchy
        jabatan_order = {
            'kepala_desa': 1,
            'sekretaris_desa': 2,
            'kaur_pemerintahan': 3,
            'kaur_pembangunan': 4,
            'kaur_kesra': 5,
            'kaur_keuangan': 6,
            'kaur_umum': 7,
            'kasi_pemerintahan': 8,
            'kasi_pembangunan': 9,
            'kasi_kesra': 10,
            'kepala_dusun': 11,
            'staf': 12,
        }
        
        perangkat_list = sorted(perangkat_list, key=lambda x: jabatan_order.get(x.jabatan, 99))
        
        paginator = Paginator(perangkat_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for perangkat in page_obj:
            results.append({
                'id': perangkat.id,
                'nama': perangkat.penduduk.name,
                'jabatan': perangkat.get_jabatan_display(),
                'jabatan_code': perangkat.jabatan,
                'nip': perangkat.nip,
                'deskripsi_tugas': perangkat.deskripsi_tugas,
                'foto_profil': perangkat.foto_profil.url if perangkat.foto_profil else None,
                'kontak_whatsapp': perangkat.kontak_whatsapp,
                'email_dinas': perangkat.email_dinas,
                'tanggal_mulai_tugas': perangkat.tanggal_mulai_tugas.isoformat() if perangkat.tanggal_mulai_tugas else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving perangkat desa data", logger)


@csrf_exempt
@require_http_methods(["GET"])
def api_lembaga_adat(request):
    """API endpoint untuk data lembaga adat - untuk public website"""
    try:
        search_query = request.GET.get('search', '')
        jenis_filter = request.GET.get('jenis', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        lembaga_list = LembagaAdat.objects.filter(status='aktif').select_related('ketua')
        
        if search_query:
            lembaga_list = lembaga_list.filter(
                Q(nama_lembaga__icontains=search_query) |
                Q(deskripsi__icontains=search_query) |
                Q(ketua__name__icontains=search_query)
            )
        
        if jenis_filter:
            lembaga_list = lembaga_list.filter(jenis_lembaga=jenis_filter)
        
        lembaga_list = lembaga_list.order_by('nama_lembaga')
        
        paginator = Paginator(lembaga_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for lembaga in page_obj:
            results.append({
                'id': lembaga.id,
                'nama_lembaga': lembaga.nama_lembaga,
                'jenis_lembaga': lembaga.get_jenis_lembaga_display(),
                'jenis_code': lembaga.jenis_lembaga,
                'ketua_nama': lembaga.ketua.name if lembaga.ketua else None,
                'deskripsi': lembaga.deskripsi,
                'kegiatan_rutin': lembaga.kegiatan_rutin,
                'jumlah_anggota': lembaga.jumlah_anggota,
                'tanggal_terbentuk': lembaga.tanggal_terbentuk.isoformat() if lembaga.tanggal_terbentuk else None,
                'alamat_sekretariat': lembaga.alamat_sekretariat,
                'kontak_phone': lembaga.kontak_phone,
                'foto_kegiatan': lembaga.foto_kegiatan.url if lembaga.foto_kegiatan else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving lembaga adat data", logger)


@csrf_exempt
@require_http_methods(["GET"])
def api_penggerak_pkk(request):
    """API endpoint untuk data penggerak PKK - untuk public website"""
    try:
        search_query = request.GET.get('search', '')
        jabatan_filter = request.GET.get('jabatan', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        pkk_list = PenggerakPKK.objects.filter(status='aktif').select_related('penduduk')
        
        if search_query:
            pkk_list = pkk_list.filter(
                Q(penduduk__name__icontains=search_query) |
                Q(jabatan__icontains=search_query) |
                Q(keahlian__icontains=search_query)
            )
        
        if jabatan_filter:
            pkk_list = pkk_list.filter(jabatan=jabatan_filter)
        
        pkk_list = pkk_list.order_by('jabatan', 'penduduk__name')
        
        paginator = Paginator(pkk_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for pkk in page_obj:
            results.append({
                'id': pkk.id,
                'nama': pkk.penduduk.name,
                'jabatan': pkk.get_jabatan_display(),
                'jabatan_code': pkk.jabatan,
                'nomor_anggota': pkk.nomor_anggota,
                'keahlian': pkk.keahlian,
                'pengalaman_organisasi': pkk.pengalaman_organisasi,
                'prestasi': pkk.prestasi,
                'foto_profil': pkk.foto_profil.url if pkk.foto_profil else None,
                'kontak_whatsapp': pkk.kontak_whatsapp,
                'tanggal_bergabung': pkk.tanggal_bergabung.isoformat() if pkk.tanggal_bergabung else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving penggerak pkk data", logger)


@csrf_exempt
@require_http_methods(["GET"])
def api_kepemudaan(request):
    """API endpoint untuk data kepemudaan - untuk public website"""
    try:
        search_query = request.GET.get('search', '')
        jenis_filter = request.GET.get('jenis', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        kepemudaan_list = Kepemudaan.objects.filter(status='aktif').select_related('ketua')
        
        if search_query:
            kepemudaan_list = kepemudaan_list.filter(
                Q(nama_organisasi__icontains=search_query) |
                Q(deskripsi__icontains=search_query) |
                Q(ketua__name__icontains=search_query)
            )
        
        if jenis_filter:
            kepemudaan_list = kepemudaan_list.filter(jenis_organisasi=jenis_filter)
        
        kepemudaan_list = kepemudaan_list.order_by('nama_organisasi')
        
        paginator = Paginator(kepemudaan_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for kepemudaan in page_obj:
            results.append({
                'id': kepemudaan.id,
                'nama_organisasi': kepemudaan.nama_organisasi,
                'jenis_organisasi': kepemudaan.get_jenis_organisasi_display(),
                'jenis_code': kepemudaan.jenis_organisasi,
                'ketua_nama': kepemudaan.ketua.name if kepemudaan.ketua else None,
                'deskripsi': kepemudaan.deskripsi,
                'kegiatan_rutin': kepemudaan.kegiatan_rutin,
                'prestasi': kepemudaan.prestasi,
                'jumlah_anggota_aktif': kepemudaan.jumlah_anggota_aktif,
                'rentang_usia': kepemudaan.rentang_usia,
                'tanggal_terbentuk': kepemudaan.tanggal_terbentuk.isoformat() if kepemudaan.tanggal_terbentuk else None,
                'alamat_sekretariat': kepemudaan.alamat_sekretariat,
                'kontak_phone': kepemudaan.kontak_phone,
                'email': kepemudaan.email,
                'foto_kegiatan': kepemudaan.foto_kegiatan.url if kepemudaan.foto_kegiatan else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving kepemudaan data", logger)


@csrf_exempt
@require_http_methods(["GET"])
def api_karang_taruna(request):
    """API endpoint untuk data karang taruna - untuk public website"""
    try:
        search_query = request.GET.get('search', '')
        jabatan_filter = request.GET.get('jabatan', '')
        pengurus_inti = request.GET.get('pengurus_inti', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        karang_taruna_list = KarangTaruna.objects.filter(status='aktif').select_related('penduduk')
        
        if search_query:
            karang_taruna_list = karang_taruna_list.filter(
                Q(penduduk__name__icontains=search_query) |
                Q(jabatan__icontains=search_query) |
                Q(bidang_keahlian__icontains=search_query)
            )
        
        if jabatan_filter:
            karang_taruna_list = karang_taruna_list.filter(jabatan=jabatan_filter)
        
        if pengurus_inti:
            karang_taruna_list = karang_taruna_list.filter(is_pengurus_inti=pengurus_inti.lower() == 'true')
        
        karang_taruna_list = karang_taruna_list.order_by('jabatan', 'penduduk__name')
        
        paginator = Paginator(karang_taruna_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for kt in page_obj:
            results.append({
                'id': kt.id,
                'nama': kt.penduduk.name,
                'jabatan': kt.get_jabatan_display(),
                'jabatan_code': kt.jabatan,
                'nomor_anggota': kt.nomor_anggota,
                'bidang_keahlian': kt.bidang_keahlian,
                'pengalaman_organisasi': kt.pengalaman_organisasi,
                'prestasi_individu': kt.prestasi_individu,
                'kontribusi': kt.kontribusi,
                'is_pengurus_inti': kt.is_pengurus_inti,
                'foto_profil': kt.foto_profil.url if kt.foto_profil else None,
                'kontak_whatsapp': kt.kontak_whatsapp,
                'email_pribadi': kt.email_pribadi,
                'pendidikan_terakhir': kt.pendidikan_terakhir,
                'pekerjaan': kt.pekerjaan,
                'tanggal_bergabung': kt.tanggal_bergabung.isoformat() if kt.tanggal_bergabung else None,
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
    except Exception as e:
        return handle_api_error(e, "retrieving karang taruna data", logger)


@csrf_exempt
@require_http_methods(["GET"])
def api_organization_structure(request):
    """API endpoint untuk struktur organisasi lengkap - untuk public website"""
    try:
        # Get all active organization data
        perangkat_desa = PerangkatDesa.objects.filter(status='aktif').select_related('penduduk')
        lembaga_adat = LembagaAdat.objects.filter(status='aktif').select_related('ketua')
        penggerak_pkk = PenggerakPKK.objects.filter(status='aktif').select_related('penduduk')
        kepemudaan = Kepemudaan.objects.filter(status='aktif').select_related('ketua')
        karang_taruna = KarangTaruna.objects.filter(status='aktif').select_related('penduduk')
        
        # Structure data for organization chart
        structure = {
            'perangkat_desa': {
                'title': 'Perangkat Desa',
                'count': perangkat_desa.count(),
                'members': []
            },
            'lembaga_adat': {
                'title': 'Lembaga Adat',
                'count': lembaga_adat.count(),
                'organizations': []
            },
            'penggerak_pkk': {
                'title': 'Penggerak PKK',
                'count': penggerak_pkk.count(),
                'members': []
            },
            'kepemudaan': {
                'title': 'Organisasi Kepemudaan',
                'count': kepemudaan.count(),
                'organizations': []
            },
            'karang_taruna': {
                'title': 'Karang Taruna',
                'count': karang_taruna.count(),
                'members': []
            }
        }
        
        # Add perangkat desa data
        for perangkat in perangkat_desa:
            structure['perangkat_desa']['members'].append({
                'nama': perangkat.penduduk.name,
                'jabatan': perangkat.get_jabatan_display(),
                'foto': perangkat.foto_profil.url if perangkat.foto_profil else None
            })
        
        # Add lembaga adat data
        for lembaga in lembaga_adat:
            structure['lembaga_adat']['organizations'].append({
                'nama': lembaga.nama_lembaga,
                'jenis': lembaga.get_jenis_lembaga_display(),
                'ketua': lembaga.ketua.name if lembaga.ketua else None,
                'anggota': lembaga.jumlah_anggota
            })
        
        # Add penggerak PKK data
        for pkk in penggerak_pkk:
            structure['penggerak_pkk']['members'].append({
                'nama': pkk.penduduk.name,
                'jabatan': pkk.get_jabatan_display(),
                'foto': pkk.foto_profil.url if pkk.foto_profil else None
            })
        
        # Add kepemudaan data
        for org in kepemudaan:
            structure['kepemudaan']['organizations'].append({
                'nama': org.nama_organisasi,
                'jenis': org.get_jenis_organisasi_display(),
                'ketua': org.ketua.name if org.ketua else None,
                'anggota': org.jumlah_anggota_aktif
            })
        
        # Add karang taruna data
        for kt in karang_taruna:
            structure['karang_taruna']['members'].append({
                'nama': kt.penduduk.name,
                'jabatan': kt.get_jabatan_display(),
                'foto': kt.foto_profil.url if kt.foto_profil else None,
                'pengurus_inti': kt.is_pengurus_inti
            })
        
        return JsonResponse({
            'success': True,
            'data': structure
        })
    except Exception as e:
        return handle_api_error(e, "retrieving organization structure", logger)