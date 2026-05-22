"""
SecureTask — Task Views
SECURITY: Every task operation scoped to request.user — prevents IDOR.
OWASP A01: Broken Access Control
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from django.views.decorators.cache import never_cache

from .models import Task
from .forms import TaskForm
from accounts.models import UserProfile
from accounts.views import log_event


# ─── Dashboard ────────────────────────────────────────────────────────────────
@login_required
@never_cache
def dashboard_view(request):
    """Summary cards and recent tasks for current user (or all tasks for admin)."""
    try:
        is_admin = request.user.profile.is_admin
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        tasks = Task.objects.select_related('owner').all()
    else:
        # SECURITY: Filter strictly by owner — OWASP A01 IDOR prevention
        tasks = Task.objects.filter(owner=request.user)

    stats = {
        'total':       tasks.count(),
        'todo':        tasks.filter(status='todo').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'completed':   tasks.filter(status='completed').count(),
        'high':        tasks.filter(priority='high').count(),
        'overdue':     sum(1 for t in tasks if t.is_overdue),
    }
    recent = tasks[:5]

    return render(request, 'tasks/dashboard.html', {
        'stats':    stats,
        'recent':   recent,
        'is_admin': is_admin,
    })


# ─── Task List ────────────────────────────────────────────────────────────────
@login_required
def task_list_view(request):
    try:
        is_admin = request.user.profile.is_admin
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        tasks = Task.objects.select_related('owner').all()
    else:
        tasks = Task.objects.filter(owner=request.user)

    # Search/filter — ORM only, injection-safe
    query    = request.GET.get('q', '').strip()[:100]    # Limit search length
    status   = request.GET.get('status', '')
    priority = request.GET.get('priority', '')

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query))
    if status in [c[0] for c in Task.STATUS_CHOICES]:
        tasks = tasks.filter(status=status)
    if priority in [c[0] for c in Task.PRIORITY_CHOICES]:
        tasks = tasks.filter(priority=priority)

    return render(request, 'tasks/task_list.html', {
        'tasks':    tasks,
        'query':    query,
        'status':   status,
        'priority': priority,
        'is_admin': is_admin,
    })


# ─── Create Task ──────────────────────────────────────────────────────────────
@login_required
@require_http_methods(['GET', 'POST'])
def task_create_view(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        # SECURITY: Force owner to current user — prevent mass assignment
        task.owner = request.user
        task.save()
        log_event(request, 'task_create', f"Task created: '{task.title}'")
        messages.success(request, "Task created successfully.")
        return redirect('task_list')

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


# ─── Edit Task ────────────────────────────────────────────────────────────────
@login_required
@require_http_methods(['GET', 'POST'])
def task_edit_view(request, pk):
    """
    SECURITY: get_object_or_404 with owner filter prevents IDOR.
    Admins can edit any task.
    OWASP A01: Broken Access Control
    """
    try:
        is_admin = request.user.profile.is_admin
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        task = get_object_or_404(Task, pk=pk)
    else:
        # IDOR protection: non-admins can only access their own tasks
        task = get_object_or_404(Task, pk=pk, owner=request.user)

    form = TaskForm(request.POST or None, instance=task)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_event(request, 'task_update', f"Task updated: '{task.title}' (ID:{pk})")
        messages.success(request, "Task updated successfully.")
        return redirect('task_list')

    return render(request, 'tasks/task_form.html', {
        'form': form, 'action': 'Edit', 'task': task})


# ─── Delete Task ──────────────────────────────────────────────────────────────
@login_required
@require_http_methods(['POST'])
def task_delete_view(request, pk):
    """
    DELETE via POST only — prevents CSRF-exploitable GET deletions.
    OWASP A01 + CSRF protection.
    """
    try:
        is_admin = request.user.profile.is_admin
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, owner=request.user)

    title = task.title
    task.delete()
    log_event(request, 'task_delete', f"Task deleted: '{title}' (ID:{pk})")
    messages.success(request, f"Task '{title}' deleted.")
    return redirect('task_list')


# ─── Mark Complete ────────────────────────────────────────────────────────────
@login_required
@require_http_methods(['POST'])
def task_complete_view(request, pk):
    try:
        is_admin = request.user.profile.is_admin
    except UserProfile.DoesNotExist:
        is_admin = False

    if is_admin:
        task = get_object_or_404(Task, pk=pk)
    else:
        task = get_object_or_404(Task, pk=pk, owner=request.user)

    task.status = 'completed'
    task.save()
    log_event(request, 'task_update', f"Task marked complete: '{task.title}'")
    messages.success(request, f"'{task.title}' marked as completed.")
    return redirect('task_list')


# ─── About / Developers Page ──────────────────────────────────────────────────
def about_view(request):
    """Public developer/team info page — no auth required."""
    team_members = [
        {
            'name':       'Luqmanul Hafiz Bin Ahmad Fairul',
            'student_id': '52215125409',
            'role':       'Lead Developer & Security Architect',
            'icon':       'fa-shield-halved',
        },
        {
            'name':       'Muhammad Iqbal Bin Ruslan',
            'student_id': '52215125730',
            'role':       'Backend Developer & Database Engineer',
            'icon':       'fa-database',
        },
        {
            'name':       'Muhammad Akmal Hakim bin Mohd Yuzlan',
            'student_id': '52215125582',
            'role':       'Frontend Developer & UI/UX Designer',
            'icon':       'fa-palette',
        },
        {
            'name':       'Muhamad Fareez Aiman bin Rozaiman',
            'student_id': '52215125751',
            'role':       'QA Engineer & Security Tester',
            'icon':       'fa-magnifying-glass-chart',
        },
    ]
    return render(request, 'pages/about.html', {'team_members': team_members})
