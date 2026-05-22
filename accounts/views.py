"""
SecureTask — Accounts Views
Handles registration, login, logout, profile, error pages.
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden

from .forms import (RegisterForm, LoginForm, ProfileUpdateForm,
                    UserProfileForm, SecurePasswordChangeForm)
from .models import UserProfile, AuditLog

logger = logging.getLogger('securetask.security')


# ─── Audit Helper ─────────────────────────────────────────────────────────────
def log_event(request, action, description, user=None):
    """
    Write to AuditLog.
    SECURITY: Never include passwords/tokens in description — OWASP A09.
    """
    ip = (request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
          or request.META.get('REMOTE_ADDR'))
    ua = request.META.get('HTTP_USER_AGENT', '')[:300]
    AuditLog.objects.create(
        user=user or (request.user if request.user.is_authenticated else None),
        action=action,
        description=description[:500],
        ip_address=ip,
        user_agent=ua,
    )
    logger.info("[AUDIT] %s | %s | %s", action, ip, description)


# ─── Registration ─────────────────────────────────────────────────────────────
@never_cache
@require_http_methods(['GET', 'POST'])
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.save()
        UserProfile.objects.create(user=user, role='user')
        log_event(request, 'register', f"New user registered: {user.username}")
        messages.success(request, "Account created! Please log in.")
        return redirect('login')

    return render(request, 'accounts/register.html', {'form': form})


# ─── Login ────────────────────────────────────────────────────────────────────
@never_cache
@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # django-axes tracks this authenticate call for brute-force
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                log_event(request, 'login_success',
                          f"Login: {user.username}", user=user)
                # Redirect to ?next= or dashboard
                next_url = request.GET.get('next', 'dashboard')
                # SECURITY: Validate next is relative — prevents open redirect
                if next_url.startswith('/') and not next_url.startswith('//'):
                    return redirect(next_url)
                return redirect('dashboard')
            else:
                # SECURITY: Generic error — don't reveal which field is wrong
                log_event(request, 'login_failed',
                          f"Failed login for username: {username}")
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, 'accounts/login.html', {'form': form})


# ─── Logout ───────────────────────────────────────────────────────────────────
@login_required
@require_http_methods(['POST'])
def logout_view(request):
    """
    SECURITY: Logout via POST only to prevent CSRF-triggered logout.
    Clears session data on logout — OWASP A07.
    """
    log_event(request, 'logout', f"Logout: {request.user.username}")
    logout(request)
    messages.success(request, "You have been logged out securely.")
    return redirect('login')


# ─── Profile ──────────────────────────────────────────────────────────────────
@login_required
@never_cache
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_form    = ProfileUpdateForm(instance=request.user)
    profile_form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        user_form    = ProfileUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            log_event(request, 'profile_update',
                      f"Profile updated by {request.user.username}")
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'accounts/profile.html', {
        'user_form':    user_form,
        'profile_form': profile_form,
    })


# ─── Password Change ──────────────────────────────────────────────────────────
@login_required
@require_http_methods(['GET', 'POST'])
def change_password_view(request):
    form = SecurePasswordChangeForm(user=request.user, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # SECURITY: Keep current user logged in after password change
        update_session_auth_hash(request, form.user)
        log_event(request, 'password_change',
                  f"Password changed by {request.user.username}")
        messages.success(request, "Password changed successfully.")
        return redirect('profile')

    return render(request, 'accounts/change_password.html', {'form': form})


# ─── Admin: User List ─────────────────────────────────────────────────────────
@login_required
def admin_users_view(request):
    """
    SECURITY: Restrict to admin role — OWASP A01 Broken Access Control.
    """
    try:
        if not request.user.profile.is_admin:
            log_event(request, 'access_denied',
                      f"{request.user.username} tried to access admin users")
            return render(request, 'errors/403.html', status=403)
    except UserProfile.DoesNotExist:
        return render(request, 'errors/403.html', status=403)

    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


# ─── Admin: Audit Logs ────────────────────────────────────────────────────────
@login_required
def audit_logs_view(request):
    """Admin-only audit log viewer."""
    try:
        if not request.user.profile.is_admin:
            log_event(request, 'access_denied',
                      f"{request.user.username} tried to access audit logs")
            return render(request, 'errors/403.html', status=403)
    except UserProfile.DoesNotExist:
        return render(request, 'errors/403.html', status=403)

    logs = AuditLog.objects.select_related('user').all()

    # Filter by action type
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)

    return render(request, 'admin_panel/audit_logs.html', {
        'logs':           logs[:200],
        'action_choices': AuditLog.ACTION_CHOICES,
        'action_filter':  action_filter,
    })


# ─── Error Handlers ───────────────────────────────────────────────────────────
def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)
