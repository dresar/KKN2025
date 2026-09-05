from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile, UMKMBusiness, WhatsAppBotConfig, SystemSettings


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'position', 'is_village_staff')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar', 'bio', 'address', 'birth_date')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class UMKMBusinessForm(forms.ModelForm):
    class Meta:
        model = UMKMBusiness
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class WhatsAppBotConfigForm(forms.ModelForm):
    class Meta:
        model = WhatsAppBotConfig
        fields = '__all__'
        widgets = {
            'welcome_message': forms.Textarea(attrs={'rows': 4}),
            'business_hours_start': forms.TimeInput(attrs={'type': 'time'}),
            'business_hours_end': forms.TimeInput(attrs={'type': 'time'}),
        }


class SystemSettingsForm(forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = '__all__'
        widgets = {
            'setting_value': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }