"""
SecureTask — REST API Serializers
SECURITY: Explicit field listing, no __all__ (prevents mass assignment).
"""
import bleach
from django.contrib.auth.models import User
from rest_framework import serializers
from tasks.models import Task
from accounts.models import AuditLog


def _sanitize(value):
    return bleach.clean(value or '', tags=[], strip=True).strip()


class TaskSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    is_overdue     = serializers.ReadOnlyField()

    class Meta:
        model  = Task
        # SECURITY: Explicit fields — prevents mass assignment of 'owner' etc.
        fields = ('id', 'title', 'description', 'priority', 'status',
                  'due_date', 'owner_username', 'is_overdue',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'owner_username', 'created_at', 'updated_at')

    def validate_title(self, value):
        value = _sanitize(value)
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value

    def validate_description(self, value):
        value = _sanitize(value)
        if len(value) > 1000:
            raise serializers.ValidationError("Max 1000 characters.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        # SECURITY: Never expose password or sensitive fields
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'date_joined', 'is_active')
        read_only_fields = ('id', 'date_joined', 'is_active')


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model  = AuditLog
        fields = ('id', 'username', 'action', 'description',
                  'ip_address', 'timestamp')
        read_only_fields = fields
