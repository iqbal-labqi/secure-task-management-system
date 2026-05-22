"""
SecureTask — Task Model
All DB access via ORM — prevents SQL injection (OWASP A03).
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]
    STATUS_CHOICES = [
        ('todo',        'To Do'),
        ('in_progress', 'In Progress'),
        ('completed',   'Completed'),
    ]

    owner       = models.ForeignKey(User, on_delete=models.CASCADE,
                                    related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, blank=True)
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES,
                                   default='medium')
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES,
                                   default='todo')
    due_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.owner.username}]"

    @property
    def is_overdue(self):
        if self.due_date and self.status != 'completed':
            return self.due_date < timezone.now().date()
        return False
