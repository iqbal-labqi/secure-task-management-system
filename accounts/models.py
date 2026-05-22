"""
SecureTask — Accounts Models
Includes UserProfile and AuditLog.
"""
import uuid
import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def profile_image_path(instance, filename):
    """
    SECURITY: Rename uploaded file with UUID to prevent path traversal
    and enumeration attacks. — OWASP A01, A04
    """
    ext = filename.rsplit('.', 1)[-1].lower()
    new_name = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('profiles', new_name)


class UserProfile(models.Model):
    """Extended user profile — one-to-one with Django's built-in User."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user',  'Normal User'),
    ]

    user        = models.OneToOneField(User, on_delete=models.CASCADE,
                                       related_name='profile')
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES,
                                   default='user')
    bio         = models.TextField(max_length=300, blank=True)
    phone       = models.CharField(max_length=20, blank=True)
    # SECURITY: File stored with UUID name, restricted MIME/ext in forms
    avatar      = models.ImageField(upload_to=profile_image_path,
                                    blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin'


class AuditLog(models.Model):
    """
    Audit trail for security-relevant events.
    SECURITY: Log actions without logging credentials — OWASP A09
    """
    ACTION_CHOICES = [
        ('login_success',  'Login Success'),
        ('login_failed',   'Login Failed'),
        ('logout',         'Logout'),
        ('register',       'Registration'),
        ('task_create',    'Task Created'),
        ('task_update',    'Task Updated'),
        ('task_delete',    'Task Deleted'),
        ('profile_update', 'Profile Updated'),
        ('password_change','Password Changed'),
        ('admin_action',   'Admin Action'),
        ('file_upload',    'File Uploaded'),
        ('access_denied',  'Access Denied'),
    ]

    # Nullable — anonymous events (e.g. failed logins) may not have a user
    user        = models.ForeignKey(User, on_delete=models.SET_NULL,
                                    null=True, blank=True,
                                    related_name='audit_logs')
    action      = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField(max_length=500)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.CharField(max_length=300, blank=True)
    timestamp   = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        who = self.user.username if self.user else 'Anonymous'
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {who} — {self.action}"
