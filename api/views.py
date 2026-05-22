"""
SecureTask — REST API Views
All endpoints authenticated. Task endpoints scoped to owner (IDOR safe).
"""
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q

from tasks.models import Task
from accounts.models import AuditLog, UserProfile
from .serializers import TaskSerializer, UserSerializer, AuditLogSerializer
from accounts.views import log_event


class IsAdminRole(permissions.BasePermission):
    """Custom permission: user must have admin role in UserProfile."""
    def has_permission(self, request, view):
        try:
            return request.user.profile.is_admin
        except Exception:
            return False


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD API for tasks.
    SECURITY:
    - Requires authentication (SessionAuth or TokenAuth)
    - get_queryset() scoped to owner → IDOR prevention — OWASP A01
    - perform_create() forces owner = request.user — prevents mass assignment
    """
    serializer_class   = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'description']
    ordering_fields    = ['created_at', 'due_date', 'priority', 'status']
    ordering           = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        try:
            is_admin = user.profile.is_admin
        except UserProfile.DoesNotExist:
            is_admin = False

        qs = Task.objects.all() if is_admin else Task.objects.filter(owner=user)

        # Optional filter params
        status_p   = self.request.query_params.get('status')
        priority_p = self.request.query_params.get('priority')
        if status_p in [c[0] for c in Task.STATUS_CHOICES]:
            qs = qs.filter(status=status_p)
        if priority_p in [c[0] for c in Task.PRIORITY_CHOICES]:
            qs = qs.filter(priority=priority_p)
        return qs

    def perform_create(self, serializer):
        # SECURITY: Force owner — user cannot set another owner
        task = serializer.save(owner=self.request.user)
        log_event(self.request, 'task_create',
                  f"API task created: '{task.title}'")

    def perform_update(self, serializer):
        task = serializer.save()
        log_event(self.request, 'task_update',
                  f"API task updated: '{task.title}' (ID:{task.pk})")

    def perform_destroy(self, instance):
        log_event(self.request, 'task_delete',
                  f"API task deleted: '{instance.title}' (ID:{instance.pk})")
        instance.delete()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        task.status = 'completed'
        task.save()
        return Response({'status': 'completed'})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin-only read-only user list."""
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset           = User.objects.all().order_by('-date_joined')


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Admin-only audit log API."""
    serializer_class   = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset           = AuditLog.objects.select_related('user').all()
    filter_backends    = [filters.SearchFilter]
    search_fields      = ['action', 'description']
