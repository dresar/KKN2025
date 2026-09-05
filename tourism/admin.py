from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    TourismCategory, TourismLocation, TourismGallery, 
    TourismReview, TourismRating, TourismEvent, 
    TourismPackage, TourismFAQ
)

@admin.register(TourismCategory)
class TourismCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['name']
    
    def color_display(self, obj):
        if obj.color:
            return format_html(
                '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 3px;"></div>',
                obj.color
            )
        return '-'
    color_display.short_description = 'Warna'

@admin.register(TourismLocation)
class TourismLocationAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'location_type', 'status', 
        'featured', 'is_active', 'average_rating_display', 
        'total_reviews_display', 'created_at'
    ]
    list_filter = [
        'category', 'location_type', 'status', 'featured', 
        'is_active', 'created_at', 'published_at'
    ]
    search_fields = ['title', 'short_description', 'address']
    list_editable = ['status', 'featured', 'is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Dasar', {
            'fields': ('title', 'slug', 'category', 'location_type', 'status')
        }),
        ('Deskripsi', {
            'fields': ('short_description', 'full_description')
        }),
        ('Lokasi', {
            'fields': ('address', 'latitude', 'longitude')
        }),
        ('Informasi Wisata', {
            'fields': ('opening_hours', 'entry_fee', 'contact_phone', 'contact_email', 'website')
        }),
        ('Fitur dan Fasilitas', {
            'fields': ('facilities', 'activities')
        }),
        ('Status dan Meta', {
            'fields': ('featured', 'is_active', 'meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Timestamps', {
            'fields': ('created_by', 'updated_by', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def average_rating_display(self, obj):
        rating = obj.average_rating
        if rating > 0:
            return format_html(
                '<span style="color: #f59e0b;">★ {:.1f}</span>',
                rating
            )
        return '-'
    average_rating_display.short_description = 'Rating Rata-rata'
    
    def total_reviews_display(self, obj):
        count = obj.total_reviews
        if count > 0:
            return format_html(
                '<span style="color: #3b82f6;">{}</span>',
                count
            )
        return '-'
    total_reviews_display.short_description = 'Total Review'
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TourismGallery)
class TourismGalleryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'package', 'media_preview', 
        'is_active', 'order', 'created_at'
    ]
    list_filter = ['package', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'package__title']
    list_editable = ['is_active', 'order']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Informasi Media', {
            'fields': ('package', 'title', 'description')
        }),
        ('File Media', {
            'fields': ('image',)
        }),
        ('Metadata', {
            'fields': ('is_active', 'order')
        }),
    )
    
    def media_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    media_preview.short_description = 'Preview Media'

@admin.register(TourismReview)
class TourismReviewAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'tourism_location', 'user', 'rating_display', 
        'visit_type', 'is_approved', 'is_flagged', 'created_at'
    ]
    list_filter = [
        'rating', 'visit_type', 'is_approved', 'is_flagged', 
        'visit_date', 'created_at'
    ]
    search_fields = ['title', 'comment', 'tourism_location__title', 'user__username']
    list_editable = ['is_approved', 'is_flagged']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Review', {
            'fields': ('tourism_location', 'user', 'rating', 'title', 'comment')
        }),
        ('Detail Kunjungan', {
            'fields': ('visit_date', 'visit_type')
        }),
        ('Moderasi', {
            'fields': ('is_approved', 'is_flagged', 'flagged_reason')
        }),
    )
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #f59e0b;">{}</span>',
            stars
        )
    rating_display.short_description = 'Rating'

@admin.register(TourismRating)
class TourismRatingAdmin(admin.ModelAdmin):
    list_display = [
        'tourism_location', 'user', 'rating_display', 'cleanliness', 
        'accessibility', 'facilities', 'service', 'value', 'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = ['tourism_location__title', 'user__username']
    ordering = ['-created_at']
    
    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #f59e0b;">{}</span>',
            stars
        )
    rating_display.short_description = 'Rating'

@admin.register(TourismEvent)
class TourismEventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'tourism_location', 'event_type', 'start_date', 
        'end_date', 'organizer', 'is_featured', 'is_active'
    ]
    list_filter = ['event_type', 'is_featured', 'is_active', 'start_date', 'end_date']
    search_fields = ['title', 'description', 'tourism_location__title', 'organizer']
    list_editable = ['is_featured', 'is_active']
    ordering = ['start_date']
    
    fieldsets = (
        ('Event', {
            'fields': ('title', 'tourism_location', 'event_type', 'description')
        }),
        ('Waktu', {
            'fields': ('start_date', 'end_date')
        }),
        ('Informasi', {
            'fields': ('organizer', 'contact_info', 'registration_required', 'registration_url')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
    )

@admin.register(TourismPackage)
class TourismPackageAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'tourism_location', 'package_type', 'duration', 
        'price', 'currency', 'max_participants', 'is_featured', 'is_active'
    ]
    list_filter = ['package_type', 'is_featured', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'tourism_location__title']
    list_editable = ['is_featured', 'is_active']
    ordering = ['price']
    
    fieldsets = (
        ('Paket', {
            'fields': ('title', 'tourism_location', 'package_type', 'description', 'duration')
        }),
        ('Harga', {
            'fields': ('price', 'currency')
        }),
        ('Fitur', {
            'fields': ('includes', 'excludes', 'itinerary')
        }),
        ('Booking', {
            'fields': ('max_participants', 'min_participants', 'booking_deadline')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
    )

@admin.register(TourismFAQ)
class TourismFAQAdmin(admin.ModelAdmin):
    list_display = [
        'question_short', 'tourism_location', 'category', 
        'order', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'tourism_location__title']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'question']
    
    def question_short(self, obj):
        return obj.question[:100] + '...' if len(obj.question) > 100 else obj.question
    question_short.short_description = 'Pertanyaan'
    
    fieldsets = (
        ('FAQ', {
            'fields': ('tourism_location', 'question', 'answer')
        }),
        ('Metadata', {
            'fields': ('category', 'order', 'is_active')
        }),
    )

# Customize admin site
admin.site.site_header = "Admin Panel Wisata Desa Pulosarok"
admin.site.site_title = "Admin Wisata"
admin.site.index_title = "Selamat Datang di Admin Panel Wisata Desa Pulosarok"
