from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.middleware.csrf import get_token
from .models import Business, BusinessCategory, Koperasi, BUMG, UKM, Aset, LayananJasa, JenisKoperasi
import json

@csrf_protect
@require_http_methods(["GET"])
def api_stats(request):
    """API endpoint untuk statistik business/UMKM"""
    try:
        stats = {
            'total_businesses': Business.objects.filter(status='aktif').count(),
            'total_categories': BusinessCategory.objects.filter(is_active=True).count(),
            'active_businesses': Business.objects.filter(status='aktif').count(),
            'business_categories': list(BusinessCategory.objects.filter(is_active=True).annotate(
                business_count=Count('business')
            ).values('name', 'business_count')[:5])
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Koperasi API Endpoints
@csrf_protect
@require_http_methods(["GET"])
def api_koperasi_list(request):
    """API endpoint for Koperasi list with pagination"""
    try:
        koperasi_list = Koperasi.objects.all()
        
        # Search functionality
        search = request.GET.get('search')
        if search:
            koperasi_list = koperasi_list.filter(
                Q(nama__icontains=search) |
                Q(alamat__icontains=search) |
                Q(ketua__icontains=search)
            )
        
        # Filter by jenis
        jenis_id = request.GET.get('jenis')
        if jenis_id:
            koperasi_list = koperasi_list.filter(jenis_koperasi_id=jenis_id)
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            koperasi_list = koperasi_list.filter(status=status)
        
        # Ordering
        ordering = request.GET.get('ordering', '-created_at')
        koperasi_list = koperasi_list.order_by(ordering)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(koperasi_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for koperasi in page_obj:
            results.append({
                'id': koperasi.id,
                'nama': koperasi.nama,
                'alamat': koperasi.alamat,
                'ketua': koperasi.ketua,
                'sekretaris': koperasi.sekretaris,
                'bendahara': koperasi.bendahara,
                'jenis_koperasi': koperasi.jenis_koperasi.nama if koperasi.jenis_koperasi else None,
                'jumlah_anggota': koperasi.jumlah_anggota,
                'modal_awal': float(koperasi.modal_awal) if koperasi.modal_awal else 0,
                'modal_sekarang': float(koperasi.modal_sekarang) if koperasi.modal_sekarang else 0,
                'nomor_badan_hukum': koperasi.nomor_badan_hukum,
                'tanggal_berdiri': koperasi.tanggal_berdiri.isoformat() if koperasi.tanggal_berdiri else None,
                'jenis_usaha': koperasi.jenis_usaha,
                'telepon': koperasi.telepon,
                'email': koperasi.email,
                'status': koperasi.status,
                'keterangan': koperasi.keterangan,
                'created_at': koperasi.created_at.isoformat()
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


# BUMG API Endpoints
@csrf_protect
@require_http_methods(["GET"])
def api_bumg_list(request):
    """API endpoint for BUMG list with pagination"""
    try:
        bumg_list = BUMG.objects.all()
        
        # Search functionality
        search = request.GET.get('search')
        if search:
            bumg_list = bumg_list.filter(
                Q(nama__icontains=search) |
                Q(alamat__icontains=search) |
                Q(direktur__icontains=search)
            )
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            bumg_list = bumg_list.filter(status=status)
        
        # Ordering
        ordering = request.GET.get('ordering', '-created_at')
        bumg_list = bumg_list.order_by(ordering)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(bumg_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for bumg in page_obj:
            results.append({
                'id': bumg.id,
                'nama': bumg.nama,
                'alamat': bumg.alamat,
                'direktur': bumg.direktur,
                'komisaris': bumg.komisaris,
                'nomor_sk': bumg.nomor_sk,
                'tanggal_sk': bumg.tanggal_sk.isoformat() if bumg.tanggal_sk else None,
                'modal_dasar': float(bumg.modal_dasar) if bumg.modal_dasar else 0,
                'modal_disetor': float(bumg.modal_disetor) if bumg.modal_disetor else 0,
                'bidang_usaha': bumg.bidang_usaha,
                'telepon': bumg.telepon,
                'email': bumg.email,
                'website': bumg.website,
                'status': bumg.status,
                'keterangan': bumg.keterangan,
                'created_at': bumg.created_at.isoformat()
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


# UKM API Endpoints
@csrf_protect
@require_http_methods(["GET"])
def api_ukm_list(request):
    """API endpoint for UKM list with pagination"""
    try:
        ukm_list = UKM.objects.all()
        
        # Search functionality
        search = request.GET.get('search')
        if search:
            ukm_list = ukm_list.filter(
                Q(nama_usaha__icontains=search) |
                Q(alamat_usaha__icontains=search) |
                Q(pemilik__icontains=search)
            )
        
        # Filter by jenis usaha
        jenis_usaha = request.GET.get('jenis_usaha')
        if jenis_usaha:
            ukm_list = ukm_list.filter(jenis_usaha__icontains=jenis_usaha)
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            ukm_list = ukm_list.filter(status=status)
        
        # Filter by skala usaha
        skala = request.GET.get('skala')
        if skala:
            ukm_list = ukm_list.filter(skala_usaha=skala)
        
        # Ordering
        ordering = request.GET.get('ordering', '-created_at')
        ukm_list = ukm_list.order_by(ordering)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(ukm_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for ukm in page_obj:
            results.append({
                'id': ukm.id,
                'nama_usaha': ukm.nama_usaha,
                'pemilik': ukm.pemilik,
                'nik_pemilik': ukm.nik_pemilik,
                'alamat_usaha': ukm.alamat_usaha,
                'alamat_pemilik': ukm.alamat_pemilik,
                'jenis_usaha': ukm.jenis_usaha,
                'skala_usaha': ukm.skala_usaha,
                'modal_awal': float(ukm.modal_awal) if ukm.modal_awal else 0,
                'omzet_bulanan': float(ukm.omzet_bulanan) if ukm.omzet_bulanan else 0,
                'jumlah_karyawan': ukm.jumlah_karyawan,
                'tanggal_mulai': ukm.tanggal_mulai.isoformat() if ukm.tanggal_mulai else None,
                'nomor_izin': ukm.nomor_izin,
                'telepon': ukm.telepon,
                'email': ukm.email,
                'produk_utama': ukm.produk_utama,
                'target_pasar': ukm.target_pasar,
                'status': ukm.status,
                'keterangan': ukm.keterangan,
                'created_at': ukm.created_at.isoformat()
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


# Aset API Endpoints
@csrf_protect
@require_http_methods(["GET"])
def api_aset_list(request):
    """API endpoint for Aset list with pagination"""
    try:
        aset_list = Aset.objects.all()
        
        # Search functionality
        search = request.GET.get('search')
        if search:
            aset_list = aset_list.filter(
                Q(nama_aset__icontains=search) |
                Q(lokasi__icontains=search) |
                Q(penanggung_jawab__icontains=search) |
                Q(kode_aset__icontains=search)
            )
        
        # Filter by kategori
        kategori = request.GET.get('kategori')
        if kategori:
            aset_list = aset_list.filter(kategori=kategori)
        
        # Filter by kondisi
        kondisi = request.GET.get('kondisi')
        if kondisi:
            aset_list = aset_list.filter(kondisi=kondisi)
        
        # Ordering
        ordering = request.GET.get('ordering', '-created_at')
        aset_list = aset_list.order_by(ordering)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(aset_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for aset in page_obj:
            results.append({
                'id': aset.id,
                'nama_aset': aset.nama_aset,
                'kategori': aset.kategori,
                'kode_aset': aset.kode_aset,
                'deskripsi': aset.deskripsi,
                'lokasi': aset.lokasi,
                'nilai_perolehan': float(aset.nilai_perolehan) if aset.nilai_perolehan else 0,
                'tanggal_perolehan': aset.tanggal_perolehan.isoformat() if aset.tanggal_perolehan else None,
                'kondisi': aset.kondisi,
                'masa_manfaat': aset.masa_manfaat,
                'penyusutan_per_tahun': float(aset.penyusutan_per_tahun) if aset.penyusutan_per_tahun else 0,
                'nilai_buku': float(aset.nilai_buku) if aset.nilai_buku else 0,
                'penanggung_jawab': aset.penanggung_jawab,
                'nomor_sertifikat': aset.nomor_sertifikat,
                'keterangan': aset.keterangan,
                'created_at': aset.created_at.isoformat()
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


# Layanan Jasa API Endpoints
@csrf_protect
@require_http_methods(["GET"])
def api_jasa_list(request):
    """API endpoint for Layanan Jasa list with pagination"""
    try:
        jasa_list = LayananJasa.objects.all()
        
        # Search functionality
        search = request.GET.get('search')
        if search:
            jasa_list = jasa_list.filter(
                Q(nama__icontains=search) |
                Q(alamat__icontains=search) |
                Q(penyedia__icontains=search)
            )
        
        # Filter by kategori
        kategori = request.GET.get('kategori')
        if kategori:
            jasa_list = jasa_list.filter(kategori=kategori)
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            jasa_list = jasa_list.filter(status=status)
        
        # Ordering
        ordering = request.GET.get('ordering', '-created_at')
        jasa_list = jasa_list.order_by(ordering)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(jasa_list, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for jasa in page_obj:
            results.append({
                'id': jasa.id,
                'nama': jasa.nama,
                'kategori': jasa.kategori,
                'deskripsi': jasa.deskripsi,
                'penyedia': jasa.penyedia,
                'telepon': jasa.telepon,
                'email': jasa.email,
                'alamat': jasa.alamat,
                'pengalaman': jasa.pengalaman,
                'harga_min': float(jasa.harga_min) if jasa.harga_min else 0,
                'harga_max': float(jasa.harga_max) if jasa.harga_max else 0,
                'satuan_harga': jasa.satuan_harga,
                'waktu_layanan': jasa.waktu_layanan,
                'area_layanan': jasa.area_layanan,
                'status': jasa.status,
                'rating': float(jasa.rating) if jasa.rating else 0,
                'website': jasa.website,
                'sertifikat': jasa.sertifikat,
                'keunggulan': jasa.keunggulan,
                'syarat_ketentuan': jasa.syarat_ketentuan,
                'created_at': jasa.created_at.isoformat()
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

@csrf_protect
@require_http_methods(["GET"])
def api_businesses(request):
    """API endpoint untuk daftar UMKM/bisnis"""
    try:
        businesses = Business.objects.filter(status='aktif')
        
        # Filtering
        business_type = request.GET.get('type')
        search = request.GET.get('search')
        ordering = request.GET.get('ordering', '-created_at')
        
        if business_type:
            businesses = businesses.filter(business_type=business_type)
        
        if search:
            businesses = businesses.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search)
            )
        
        # Ordering
        businesses = businesses.order_by(ordering)
        
        # Pagination
        page_size = int(request.GET.get('page_size', 10))
        page = int(request.GET.get('page', 1))
        
        paginator = Paginator(businesses, page_size)
        page_obj = paginator.get_page(page)
        
        results = []
        for business in page_obj:
            results.append({
                'id': business.id,
                'name': business.name,
                'description': business.description,
                'phone': business.phone,
                'email': business.email,
                'address': business.address,
                'business_type': business.business_type,
                'category': {
                    'id': business.category.id,
                    'name': business.category.name
                } if business.category else None,
                'status': business.status,
                'established_date': business.established_date.isoformat() if business.established_date else None,
                'created_at': business.created_at.isoformat()
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

@csrf_protect
@require_http_methods(["GET"])
def api_business_detail(request, business_id):
    """API endpoint untuk detail UMKM/bisnis"""
    try:
        business = Business.objects.get(id=business_id, is_active=True)
        
        data = {
            'id': business.id,
            'name': business.name,
            'description': business.description,
            'owner_name': business.owner_name,
            'phone': business.phone,
            'email': business.email,
            'address': business.address,
            'website': business.website,
            'social_media': business.social_media,
            'business_type': {
                'id': business.business_type.id,
                'name': business.business_type.name,
                'description': business.business_type.description
            } if business.business_type else None,
            'status': business.status,
            'featured': business.featured,
            'logo': business.logo.url if business.logo else None,
            'established_date': business.established_date.isoformat() if business.established_date else None,
            'employee_count': business.employee_count,
            'annual_revenue': float(business.annual_revenue) if business.annual_revenue else None,
            'products_services': business.products_services,
            'created_at': business.created_at.isoformat()
        }
        
        return JsonResponse(data)
    except Business.DoesNotExist:
        return JsonResponse({'error': 'Business not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)