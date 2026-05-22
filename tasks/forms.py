"""
SecureTask — Task Forms
Server-side validation for all task fields — OWASP A03.
"""
import bleach
from django import forms
from django.utils import timezone
from .models import Task


def _sanitize(value):
    """Strip HTML to prevent stored XSS — OWASP A03."""
    return bleach.clean(value, tags=[], strip=True).strip()


class TaskForm(forms.ModelForm):
    class Meta:
        model  = Task
        fields = ('title', 'description', 'priority', 'status', 'due_date')
        widgets = {
            'due_date':    forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4, 'maxlength': 1000}),
        }

    def clean_title(self):
        title = _sanitize(self.cleaned_data.get('title', ''))
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        if len(title) > 200:
            raise forms.ValidationError("Title cannot exceed 200 characters.")
        return title

    def clean_description(self):
        desc = _sanitize(self.cleaned_data.get('description', ''))
        if len(desc) > 1000:
            raise forms.ValidationError("Description cannot exceed 1000 characters.")
        return desc

    def clean_due_date(self):
        due = self.cleaned_data.get('due_date')
        if due and due < timezone.now().date():
            raise forms.ValidationError("Due date cannot be in the past.")
        return due

    def clean_priority(self):
        priority = self.cleaned_data.get('priority')
        valid = [c[0] for c in Task.PRIORITY_CHOICES]
        if priority not in valid:
            raise forms.ValidationError("Invalid priority value.")
        return priority

    def clean_status(self):
        status = self.cleaned_data.get('status')
        valid = [c[0] for c in Task.STATUS_CHOICES]
        if status not in valid:
            raise forms.ValidationError("Invalid status value.")
        return status
