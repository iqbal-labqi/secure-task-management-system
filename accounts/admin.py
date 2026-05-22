from django.contrib import admin
from .models import UserProfile, AuditLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'role', 'created_at')
    list_filter   = ('role',)
    search_fields = ('user__username', 'user__email')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ('timestamp', 'user', 'action', 'ip_address')
    list_filter   = ('action',)
    search_fields = ('user__username', 'description')
    readonly_fields = ('timestamp', 'user', 'action', 'description',
                       'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False  # Logs are system-generated only

    def has_change_permission(self, request, obj=None):
        return False  # Immutable audit records
