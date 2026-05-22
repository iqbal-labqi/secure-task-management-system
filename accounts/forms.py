"""
SecureTask — Accounts Forms
All forms validate server-side. OWASP A03, A04, A07.
"""
import magic
import bleach
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.conf import settings
from .models import UserProfile


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _clean_text(value):
    """Strip HTML/dangerous chars — OWASP A03 XSS prevention."""
    return bleach.clean(value, tags=[], strip=True).strip()


# ─── Registration ─────────────────────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    """
    User registration with strong validation.
    SECURITY: Validates email, username format, and password strength.
    """
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=True)

    class Meta:
        model  = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'password1', 'password2')

    def clean_username(self):
        username = _clean_text(self.cleaned_data.get('username', ''))
        # Only allow alphanumeric + underscores — OWASP A03
        if not username.replace('_', '').isalnum():
            raise forms.ValidationError(
                "Username may only contain letters, numbers, and underscores.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_first_name(self):
        return _clean_text(self.cleaned_data.get('first_name', ''))

    def clean_last_name(self):
        return _clean_text(self.cleaned_data.get('last_name', ''))


# ─── Login ────────────────────────────────────────────────────────────────────
class LoginForm(forms.Form):
    """Login form — simple, no exposure of which field is wrong."""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        return _clean_text(self.cleaned_data.get('username', ''))


# ─── Profile Update ───────────────────────────────────────────────────────────
class ProfileUpdateForm(forms.ModelForm):
    """Update basic User fields."""
    first_name = forms.CharField(max_length=50, required=False)
    last_name  = forms.CharField(max_length=50, required=False)
    email      = forms.EmailField(required=True)

    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("That email is in use by another account.")
        return email

    def clean_first_name(self):
        return _clean_text(self.cleaned_data.get('first_name', ''))

    def clean_last_name(self):
        return _clean_text(self.cleaned_data.get('last_name', ''))


class UserProfileForm(forms.ModelForm):
    """Update UserProfile fields (bio, phone, avatar)."""
    class Meta:
        model  = UserProfile
        fields = ('bio', 'phone', 'avatar')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'maxlength': 300}),
        }

    def clean_bio(self):
        return _clean_text(self.cleaned_data.get('bio', ''))

    def clean_phone(self):
        phone = _clean_text(self.cleaned_data.get('phone', ''))
        # Allow digits, spaces, +, -, ()
        allowed = set('0123456789 +-+()')
        if phone and not all(c in allowed for c in phone):
            raise forms.ValidationError("Invalid phone number format.")
        return phone

    def clean_avatar(self):
        """
        SECURITY: Validate uploaded image file.
        - Check extension whitelist
        - Check MIME type via python-magic (not just Content-Type header)
        - Enforce max file size
        OWASP A04: Insecure Design / File Upload
        """
        avatar = self.cleaned_data.get('avatar')
        if not avatar:
            return avatar

        # Size check
        if avatar.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            raise forms.ValidationError("Image must be smaller than 2 MB.")

        # Extension check
        ext = avatar.name.rsplit('.', 1)[-1].lower() if '.' in avatar.name else ''
        if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
            raise forms.ValidationError(
                f"Allowed types: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}")

        # MIME type check via file content — not just extension
        mime = magic.from_buffer(avatar.read(2048), mime=True)
        avatar.seek(0)   # Reset file pointer after reading
        if mime not in settings.ALLOWED_IMAGE_MIMES:
            raise forms.ValidationError("File content does not match an allowed image type.")

        return avatar


# ─── Password Change ──────────────────────────────────────────────────────────
class SecurePasswordChangeForm(PasswordChangeForm):
    """
    Wraps Django's PasswordChangeForm — inherits all password validators.
    SECURITY: Old password required before change — OWASP A07
    """
    pass
