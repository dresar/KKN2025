from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, UMKMBusiness, WhatsAppBotConfig, SystemSettings


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'position', 'is_village_staff', 'is_active')
    list_filter = ('is_village_staff', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'position')
    fieldsets = UserAdmin.fieldsets + (
        ('Village Info', {'fields': ('phone_number', 'position', 'is_village_staff')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at',)


@admin.register(UMKMBusiness)
class UMKMBusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'business_type', 'phone_number', 'is_active', 'created_at')
    list_filter = ('business_type', 'is_active', 'created_at')
    search_fields = ('name', 'owner_name', 'business_type', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WhatsAppBotConfig)
class WhatsAppBotConfigAdmin(admin.ModelAdmin):
    list_display = ('bot_name', 'business_hours_start', 'business_hours_end', 'auto_reply_enabled', 'is_active')
    list_filter = ('auto_reply_enabled', 'is_active')
    search_fields = ('bot_name',)


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('setting_key', 'setting_value', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('setting_key', 'setting_value')
    readonly_fields = ('created_at', 'updated_at')
