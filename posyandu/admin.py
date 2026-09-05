from django.contrib import admin
from .models import PosyanduLocation, PosyanduSchedule, HealthRecord, Immunization, NutritionData


@admin.register(PosyanduLocation)
class PosyanduLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'coordinator', 'capacity', 'is_active', 'established_date')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'coordinator__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('coordinator',)


@admin.register(PosyanduSchedule)
class PosyanduScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'activity_type', 'schedule_date', 'is_completed')
    list_filter = ('activity_type', 'is_completed', 'location')
    search_fields = ('title', 'description', 'location__name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'schedule_date'


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'posyandu', 'patient_type', 'visit_date', 'weight', 'height')
    list_filter = ('patient_type', 'posyandu', 'visit_date')
    search_fields = ('patient__name', 'posyandu__name', 'diagnosis')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient',)
    date_hierarchy = 'visit_date'


@admin.register(Immunization)
class ImmunizationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'vaccine_name', 'dose_number', 'immunization_date', 'posyandu')
    list_filter = ('vaccine_type', 'posyandu', 'immunization_date')
    search_fields = ('patient__name', 'vaccine_name', 'posyandu__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient',)
    date_hierarchy = 'immunization_date'


@admin.register(NutritionData)
class NutritionDataAdmin(admin.ModelAdmin):
    list_display = ('patient', 'measurement_date', 'age_months', 'weight', 'height', 'nutrition_status')
    list_filter = ('nutrition_status', 'posyandu', 'vitamin_a_given', 'iron_supplement_given')
    search_fields = ('patient__name', 'posyandu__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('patient',)
    date_hierarchy = 'measurement_date'
