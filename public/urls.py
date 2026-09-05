from django.urls import path, include
from . import views

app_name = 'public'

urlpatterns = [
    # API endpoints
    path('api/', include('public.api_urls')),
    
    # Public pages
    path('', views.public_home, name='home'),
    path('profil/', views.public_profile, name='profile'),
    path('profil/visi-misi/', views.public_profile, name='profile_vision'),
    path('profil/sejarah/', views.public_profile, name='profile_history'),
    path('profil/geografis/', views.public_profile, name='profile_geography'),
    path('profil/peta/', views.public_profile, name='profile_map'),
    path('penduduk/', views.public_population, name='population'),
    path('kegiatan/', views.public_events, name='events'),
    path('berita/', views.public_news, name='news'),
    path('wisata/', views.public_tourism, name='tourism'),
    path('umkm/', views.public_umkm, name='umkm'),
    path('organisasi/', views.public_organization, name='organization'),
    path('layanan/', views.public_correspondence, name='correspondence'),
    path('kontak/', views.public_contact, name='contact'),
]