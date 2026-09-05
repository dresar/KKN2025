from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    """Extended user model for village staff"""
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    is_village_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.position}"


class UserProfile(models.Model):
    """Additional profile information for users"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class UMKMBusiness(models.Model):
    """UMKM business data for WhatsApp bot integration"""
    name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    business_type = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    whatsapp_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.owner_name}"


class WhatsAppBotConfig(models.Model):
    """Configuration for WhatsApp bot integration"""
    bot_name = models.CharField(max_length=100)
    welcome_message = models.TextField()
    business_hours_start = models.TimeField()
    business_hours_end = models.TimeField()
    auto_reply_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bot Config: {self.bot_name}"


class SystemSettings(models.Model):
    """General system settings"""
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.TextField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.setting_key}: {self.setting_value[:50]}"


class WebsiteSettings(models.Model):
    """Website configuration settings"""
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System)')
    ]
    
    LANGUAGE_CHOICES = [
        ('id', 'Bahasa Indonesia'),
        ('en', 'English'),
        ('jv', 'Bahasa Jawa')
    ]
    
    # Basic Website Info
    site_name = models.CharField(max_length=200, default='Website Desa Pulosarok')
    site_description = models.TextField(default='Sistem Informasi Desa Pulosarok')
    site_logo = models.ImageField(upload_to='website/', blank=True, null=True)
    site_favicon = models.ImageField(upload_to='website/', blank=True, null=True)
    
    # Contact Information
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_address = models.TextField(blank=True, null=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    # Appearance
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    primary_color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#10B981')
    
    # Localization
    default_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='id')
    timezone = models.CharField(max_length=50, default='Asia/Jakarta')
    
    # SEO Settings
    meta_keywords = models.TextField(blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    google_analytics_id = models.CharField(max_length=50, blank=True, null=True)
    
    # System Settings
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, null=True)
    allow_registration = models.BooleanField(default=False)
    max_file_upload_size = models.IntegerField(default=10)  # MB
    
    # Notification Settings
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    whatsapp_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Website Settings'
        verbose_name_plural = 'Website Settings'
    
    def __str__(self):
        return f"Website Settings - {self.site_name}"


class ModuleSettings(models.Model):
    """Settings for individual modules"""
    MODULE_CHOICES = [
        ('core', 'Core Module'),
        ('references', 'References Module'),
        ('events', 'Events Module'),
        ('documents', 'Documents Module'),
        ('business', 'Business Module'),
        ('village_profile', 'Village Profile Module'),
        ('posyandu', 'Posyandu Module'),
        ('letters', 'Letters Module'),
        ('beneficiaries', 'Beneficiaries Module'),
        ('organization', 'Organization Module'),
        ('news', 'News Module'),
        ('tourism', 'Tourism Module'),
    ]
    
    module_name = models.CharField(max_length=50, choices=MODULE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_visible_in_menu = models.BooleanField(default=True)
    menu_order = models.IntegerField(default=0)
    icon_class = models.CharField(max_length=50, default='fas fa-cog')
    
    # Permissions
    requires_permission = models.BooleanField(default=False)
    required_permission = models.CharField(max_length=100, blank=True, null=True)
    
    # API Settings
    api_enabled = models.BooleanField(default=True)
    api_rate_limit = models.IntegerField(default=100)  # requests per minute
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['menu_order', 'display_name']
        verbose_name = 'Module Settings'
        verbose_name_plural = 'Module Settings'
    
    def __str__(self):
        return f"{self.display_name} ({'Active' if self.is_active else 'Inactive'})"


class APIEndpoint(models.Model):
    """Registry of all API endpoints"""
    module = models.ForeignKey(ModuleSettings, on_delete=models.CASCADE, related_name='api_endpoints')
    name = models.CharField(max_length=100)
    url_pattern = models.CharField(max_length=200)
    method = models.CharField(max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH')
    ])
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    requires_auth = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['module', 'url_pattern', 'method']
        verbose_name = 'API Endpoint'
        verbose_name_plural = 'API Endpoints'
    
    def __str__(self):
        return f"{self.method} {self.url_pattern}"


class Message(models.Model):
    """Model untuk pesan dari pengunjung website"""
    name = models.CharField(max_length=100, verbose_name='Nama')
    email = models.EmailField(verbose_name='Email')
    subject = models.CharField(max_length=200, verbose_name='Subjek')
    message = models.TextField(verbose_name='Pesan')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name='Sudah Dibaca')
    
    class Meta:
        verbose_name = 'Pesan'
        verbose_name_plural = 'Pesan'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
