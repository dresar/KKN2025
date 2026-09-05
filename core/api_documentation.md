# API Documentation - Pulosarok Website

## Overview
Dokumentasi lengkap API endpoints dari semua modul dalam sistem website Pulosarok.

## Core Module APIs

### Statistics
- `GET /core/stats/` - Statistik core module

### User Management
- `GET /core/users/` - List users dengan pagination dan search
- `GET /core/users/{user_id}/` - Detail user
- `POST /core/users/create/` - Buat user baru
- `PUT /core/users/{user_id}/update/` - Update user
- `DELETE /core/users/{user_id}/delete/` - Hapus user

### UMKM Management
- `GET /core/umkm/` - List UMKM
- `GET /core/umkm/{umkm_id}/` - Detail UMKM
- `POST /core/umkm/create/` - Buat UMKM baru
- `PUT /core/umkm/{umkm_id}/update/` - Update UMKM
- `DELETE /core/umkm/{umkm_id}/delete/` - Hapus UMKM

### System Settings
- `GET /core/settings/` - List system settings
- `GET /core/settings/{setting_id}/` - Detail setting
- `POST /core/settings/create/` - Buat setting baru
- `PUT /core/settings/{setting_id}/update/` - Update setting
- `DELETE /core/settings/{setting_id}/delete/` - Hapus setting

## References Module APIs

### Penduduk (Population)
- `GET /references/penduduk/` - List penduduk
- `POST /references/penduduk/create/` - Tambah penduduk
- `GET /references/penduduk/{id}/` - Detail penduduk
- `PUT /references/penduduk/{id}/update/` - Update penduduk
- `DELETE /references/penduduk/{id}/delete/` - Hapus penduduk
- `GET /references/penduduk/export/` - Export data penduduk

### Dusun & Lorong
- `GET /references/dusun/` - List dusun
- `POST /references/dusun/create/` - Tambah dusun
- `GET /references/lorong/` - List lorong
- `POST /references/lorong/create/` - Tambah lorong

### Disabilitas
- `GET /references/disabilitas-type/` - List tipe disabilitas
- `GET /references/disabilitas-data/` - List data disabilitas

### Family
- `GET /references/family/` - List keluarga
- `POST /references/family/create/` - Tambah keluarga

## Events Module APIs

### Events Management
- `GET /events/api/stats/` - Statistik events
- `GET /events/api/events/` - List events
- `POST /events/api/events/create/` - Buat event baru
- `GET /events/api/events/{event_id}/` - Detail event
- `PUT /events/api/events/{event_id}/update/` - Update event
- `DELETE /events/api/events/{event_id}/delete/` - Hapus event

### Categories
- `GET /events/api/categories/` - List kategori event
- `POST /events/api/categories/create/` - Buat kategori baru

### Participants
- `GET /events/api/participants/` - List peserta
- `POST /events/api/participants/create/` - Tambah peserta

## Documents Module APIs

### Document Types
- `GET /documents/types/` - List tipe dokumen
- `POST /documents/types/create/` - Buat tipe dokumen
- `GET /documents/types/{pk}/` - Detail tipe dokumen
- `PUT /documents/types/{pk}/update/` - Update tipe dokumen
- `DELETE /documents/types/{pk}/delete/` - Hapus tipe dokumen

### Documents
- `GET /documents/documents/` - List dokumen
- `POST /documents/documents/create/` - Buat dokumen
- `GET /documents/documents/{pk}/` - Detail dokumen
- `PUT /documents/documents/{pk}/update/` - Update dokumen
- `DELETE /documents/documents/{pk}/delete/` - Hapus dokumen

### Document Requests
- `GET /documents/requests/` - List permintaan dokumen

### Templates
- `GET /documents/templates/` - List template dokumen

### Statistics
- `GET /documents/statistics/` - Statistik dokumen

### Dropdowns
- `GET /documents/types/dropdown/` - Dropdown tipe dokumen
- `GET /documents/residents/dropdown/` - Dropdown penduduk
- `GET /documents/documents/dropdown/` - Dropdown dokumen

## Business Module APIs

### Business Categories
- `GET /business/categories/` - List kategori bisnis
- `POST /business/categories/create/` - Buat kategori bisnis
- `GET /business/categories/{pk}/` - Detail kategori
- `PUT /business/categories/{pk}/update/` - Update kategori
- `DELETE /business/categories/{pk}/delete/` - Hapus kategori

### Businesses
- `GET /business/businesses/` - List bisnis
- `POST /business/businesses/create/` - Buat bisnis
- `GET /business/businesses/{pk}/` - Detail bisnis
- `PUT /business/businesses/{pk}/update/` - Update bisnis
- `DELETE /business/businesses/{pk}/delete/` - Hapus bisnis

## Village Profile Module APIs

### Vision & Mission
- `GET /village_profile/vision/` - List visi misi
- `POST /village_profile/vision/add/` - Tambah visi misi
- `GET /village_profile/vision/{pk}/` - Detail visi misi
- `PUT /village_profile/vision/{pk}/edit/` - Update visi misi
- `DELETE /village_profile/vision/{pk}/delete/` - Hapus visi misi

### History
- `GET /village_profile/history/` - List sejarah
- `POST /village_profile/history/add/` - Tambah sejarah
- `GET /village_profile/history/{pk}/` - Detail sejarah
- `PUT /village_profile/history/{pk}/edit/` - Update sejarah
- `DELETE /village_profile/history/{pk}/delete/` - Hapus sejarah

### Maps
- `GET /village_profile/maps/` - List peta
- `POST /village_profile/maps/add/` - Tambah peta
- `GET /village_profile/maps/{pk}/` - Detail peta
- `PUT /village_profile/maps/{pk}/edit/` - Update peta
- `DELETE /village_profile/maps/{pk}/delete/` - Hapus peta

## Posyandu Module APIs

### Locations
- `GET /posyandu/api/locations/` - List lokasi posyandu
- `POST /posyandu/api/locations/create/` - Buat lokasi posyandu
- `GET /posyandu/api/locations/{location_id}/` - Detail lokasi
- `PUT /posyandu/api/locations/{location_id}/update/` - Update lokasi
- `DELETE /posyandu/api/locations/{location_id}/delete/` - Hapus lokasi

### Schedules
- `GET /posyandu/api/schedules/` - List jadwal posyandu
- `POST /posyandu/api/schedules/create/` - Buat jadwal
- `GET /posyandu/api/schedules/{schedule_id}/` - Detail jadwal
- `PUT /posyandu/api/schedules/{schedule_id}/update/` - Update jadwal
- `DELETE /posyandu/api/schedules/{schedule_id}/delete/` - Hapus jadwal

## Letters Module APIs

### Letter Types
- `GET /letters/letter-types/` - List tipe surat
- `POST /letters/letter-types/create/` - Buat tipe surat
- `GET /letters/letter-types/{pk}/` - Detail tipe surat
- `PUT /letters/letter-types/{pk}/update/` - Update tipe surat
- `DELETE /letters/letter-types/{pk}/delete/` - Hapus tipe surat

### Letters
- `GET /letters/letters/` - List surat
- `POST /letters/letters/create/` - Buat surat
- `GET /letters/letters/{pk}/` - Detail surat
- `PUT /letters/letters/{pk}/update/` - Update surat
- `DELETE /letters/letters/{pk}/delete/` - Hapus surat

### Export
- `GET /letters/{letter_id}/export/pdf/` - Export surat ke PDF
- `GET /letters/{letter_id}/export/docx/` - Export surat ke DOCX

## Beneficiaries Module APIs

### Beneficiary Categories
- `GET /beneficiaries/categories/` - List kategori penerima bantuan
- `POST /beneficiaries/categories/create/` - Buat kategori
- `GET /beneficiaries/categories/{pk}/` - Detail kategori
- `PUT /beneficiaries/categories/{pk}/update/` - Update kategori
- `DELETE /beneficiaries/categories/{pk}/delete/` - Hapus kategori

### Beneficiaries
- `GET /beneficiaries/beneficiaries/` - List penerima bantuan
- `POST /beneficiaries/beneficiaries/create/` - Buat penerima bantuan
- `GET /beneficiaries/beneficiaries/{pk}/` - Detail penerima bantuan
- `PUT /beneficiaries/beneficiaries/{pk}/update/` - Update penerima bantuan
- `DELETE /beneficiaries/beneficiaries/{pk}/delete/` - Hapus penerima bantuan

### Aid Programs
- `GET /beneficiaries/programs/` - List program bantuan
- `POST /beneficiaries/programs/create/` - Buat program bantuan
- `GET /beneficiaries/programs/{pk}/` - Detail program bantuan
- `PUT /beneficiaries/programs/{pk}/update/` - Update program bantuan
- `DELETE /beneficiaries/programs/{pk}/delete/` - Hapus program bantuan

## Custom Admin APIs

### Dashboard
- `GET /custom_admin/dashboard-stats/` - Statistik dashboard
- `GET /custom_admin/recent-activities/` - Aktivitas terbaru
- `GET /custom_admin/system-info/` - Informasi sistem
- `GET /custom_admin/search/` - Pencarian global

### Module Management
- `GET /custom_admin/module/{module_name}/` - View modul tertentu

## Response Format

Semua API menggunakan format response JSON standar:

### Success Response
```json
{
    "success": true,
    "data": {},
    "message": "Success message"
}
```

### Error Response
```json
{
    "success": false,
    "message": "Error message",
    "errors": {}
}
```

### Pagination Response
```json
{
    "results": [],
    "pagination": {
        "current_page": 1,
        "total_pages": 10,
        "total_items": 100,
        "has_previous": false,
        "has_next": true
    }
}
```

## Authentication

Semua API endpoint memerlukan autentikasi kecuali yang disebutkan khusus. Gunakan Django session authentication atau token authentication.

## Rate Limiting

API memiliki rate limiting untuk mencegah abuse:
- 100 requests per menit untuk user biasa
- 1000 requests per menit untuk admin

## Error Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error