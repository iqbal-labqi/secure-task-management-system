"""
Usage: python manage.py seed_demo
Creates admin + demo user with sample tasks for quick testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from tasks.models import Task
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = 'Seed demo admin and user accounts with sample tasks'

    def handle(self, *args, **kwargs):
        # Admin
        admin, created = User.objects.get_or_create(username='admin')
        if created:
            admin.set_password('Admin@1234')
            admin.email = 'admin@securetask.dev'
            admin.first_name = 'Admin'
            admin.last_name = 'User'
            admin.save()
        profile, _ = UserProfile.objects.get_or_create(user=admin)
        profile.role = 'admin'
        profile.save()

        # Demo user
        demo, created = User.objects.get_or_create(username='demouser')
        if created:
            demo.set_password('Demo@1234')
            demo.email = 'demo@securetask.dev'
            demo.first_name = 'Demo'
            demo.last_name = 'User'
            demo.save()
        UserProfile.objects.get_or_create(user=demo, defaults={'role': 'user'})

        # Sample tasks
        today = timezone.now().date()
        samples = [
            ('Set up MySQL database', 'Configure the MySQL connection.', 'high', 'completed',
             today - datetime.timedelta(days=5)),
            ('Implement RBAC', 'Role-based access control for admin and users.', 'high', 'completed',
             today - datetime.timedelta(days=3)),
            ('Write API serializers', 'DRF serializers for tasks and audit logs.', 'medium', 'in_progress',
             today + datetime.timedelta(days=2)),
            ('Frontend dashboard', 'Build Bootstrap 5 dashboard with stat cards.', 'medium', 'in_progress',
             today + datetime.timedelta(days=4)),
            ('Security testing', 'Run OWASP ZAP scan on staging environment.', 'high', 'todo',
             today + datetime.timedelta(days=7)),
            ('Write documentation', 'README and API docs.', 'low', 'todo',
             today + datetime.timedelta(days=10)),
        ]
        for title, desc, pri, status, due in samples:
            Task.objects.get_or_create(
                owner=demo, title=title,
                defaults={'description': desc, 'priority': pri,
                          'status': status, 'due_date': due}
            )

        self.stdout.write(self.style.SUCCESS(
            '\nDemo data seeded!\n'
            '  Admin   → username: admin    password: Admin@1234\n'
            '  User    → username: demouser password: Demo@1234\n'
        ))
