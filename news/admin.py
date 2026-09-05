from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    NewsCategory,
    NewsTag,
    News,
    NewsComment,
    NewsView,
    NewsImage,
    NewsLike,
    NewsShare
)


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(NewsTag)
class NewsTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    readonly_fields = ['slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
    fields = ['image', 'caption', 'alt_text', 'is_featured', 'order']
    readonly_fields = ['thumbnail']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status_badge', 'priority_badge', 'is_featured', 'is_breaking', 'published_date', 'stats_display']
    list_filter = ['status', 'priority', 'category', 'is_featured', 'is_breaking', 'published_date', 'created_at']
    search_fields = ['title', 'content', 'author__username', 'author__first_name', 'author__last_name']
    readonly_fields = ['slug', 'get_views_count', 'get_likes_count', 'comments_count', 'get_shares_count', 'reading_time', 'created_at', 'updated_at']
    raw_id_fields = ['author']
    filter_horizontal = ['tags']
    date_hierarchy = 'published_date'
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-published_date', '-created_at']
    inlines = [NewsImageInline]
    
    fieldsets = (
        ('Informasi Berita', {
            'fields': ('title', 'slug', 'category', 'tags', 'author')
        }),
        ('Konten', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('Status & Penjadwalan', {
            'fields': ('status', 'priority', 'is_featured', 'is_breaking', 'published_date', 'scheduled_date')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Statistik', {
            'fields': ('get_views_count', 'get_likes_count', 'comments_count', 'get_shares_count', 'reading_time'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'scheduled': 'blue',
            'published': 'green',
            'archived': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        colors = {
            'low': '#6B7280',
            'normal': '#3B82F6',
            'high': '#F59E0B',
            'urgent': '#EF4444'
        }
        color = colors.get(obj.priority, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioritas'
    
    def stats_display(self, obj):
        return format_html(
            '<div style="font-size: 11px;">👁 {} | ❤ {} | 💬 {} | 📤 {}</div>',
            obj.views_count, obj.likes_count, obj.comments_count, obj.shares_count
        )
    stats_display.short_description = 'Statistik'
    
    actions = ['make_published', 'make_draft', 'make_archived', 'update_counts']
    
    def make_published(self, request, queryset):
        updated = queryset.update(status='published', published_date=timezone.now())
        self.message_user(request, f'{updated} berita berhasil dipublikasi.')
    make_published.short_description = 'Publikasikan berita terpilih'
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} berita berhasil dijadikan draft.')
    make_draft.short_description = 'Jadikan draft'
    
    def make_archived(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} berita berhasil diarsipkan.')
    make_archived.short_description = 'Arsipkan berita terpilih'
    
    def update_counts(self, request, queryset):
        for news in queryset:
            news.update_counts()
        self.message_user(request, f'Statistik {queryset.count()} berita berhasil diperbarui.')
    update_counts.short_description = 'Perbarui statistik'


@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'news', 'status', 'is_author_verified', 'created_at']
    list_filter = ['status', 'is_author_verified', 'created_at']
    search_fields = ['author_name', 'author_email', 'content', 'news__title']
    readonly_fields = ['ip_address', 'user_agent', 'created_at', 'updated_at']
    raw_id_fields = ['news', 'parent']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informasi Komentar', {
            'fields': ('news', 'author_name', 'author_email', 'author_website')
        }),
        ('Konten & Status', {
            'fields': ('content', 'status', 'parent', 'is_author_verified')
        }),
        ('Informasi Teknis', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(NewsView)
class NewsViewAdmin(admin.ModelAdmin):
    list_display = ['news', 'ip_address', 'user', 'view_date', 'view_duration', 'device_type', 'browser']
    list_filter = ['view_date', 'device_type', 'browser', 'operating_system']
    search_fields = ['news__title', 'ip_address', 'user__username']
    readonly_fields = ['news', 'ip_address', 'user_agent', 'referrer', 'session_key', 'user', 'view_date', 'view_duration', 'device_type', 'browser', 'operating_system']
    raw_id_fields = ['news', 'user']
    date_hierarchy = 'view_date'
    ordering = ['-view_date']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ['news', 'image_preview', 'caption', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'created_at']
    search_fields = ['news__title', 'caption', 'alt_text']
    readonly_fields = ['thumbnail', 'created_at']
    raw_id_fields = ['news']
    ordering = ['news', 'order', 'created_at']
    
    def image_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.thumbnail.url)
        elif obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return 'No Image'
    image_preview.short_description = 'Preview'


@admin.register(NewsLike)
class NewsLikeAdmin(admin.ModelAdmin):
    list_display = ['news', 'user_display', 'ip_address', 'created_at']
    list_filter = ['created_at']
    search_fields = ['news__title', 'user__username', 'ip_address']
    readonly_fields = ['news', 'user', 'ip_address', 'session_key', 'user_agent', 'created_at']
    raw_id_fields = ['news', 'user']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def user_display(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    user_display.short_description = 'User'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(NewsShare)
class NewsShareAdmin(admin.ModelAdmin):
    list_display = ['news', 'platform_badge', 'user_display', 'ip_address', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['news__title', 'user__username', 'ip_address']
    readonly_fields = ['news', 'platform', 'user', 'ip_address', 'session_key', 'user_agent', 'referrer', 'created_at']
    raw_id_fields = ['news', 'user']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def platform_badge(self, obj):
        colors = {
            'facebook': '#1877F2',
            'twitter': '#1DA1F2',
            'whatsapp': '#25D366',
            'telegram': '#0088CC',
            'email': '#EA4335',
            'copy_link': '#6B7280',
            'other': '#9CA3AF'
        }
        color = colors.get(obj.platform, '#6B7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_platform_display()
        )
    platform_badge.short_description = 'Platform'
    
    def user_display(self, obj):
        return obj.user.username if obj.user else 'Anonymous'
    user_display.short_description = 'User'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
