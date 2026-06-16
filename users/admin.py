from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailVerification


@admin.register(User)
class TajflixUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'is_email_verified', 'is_premium', 'is_active', 'date_joined']
    list_filter = ['is_email_verified', 'is_premium', 'is_active', 'is_staff']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_editable = ['is_premium', 'is_active']

    fieldsets = UserAdmin.fieldsets + (
        ('Tajflix', {'fields': ('avatar', 'bio', 'is_premium', 'is_email_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Основное', {'fields': ('email',)}),
    )


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used']
    search_fields = ['user__email']
    readonly_fields = ['token', 'created_at']
