"""
SecureTask — Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler403 = 'accounts.views.error_403'
handler404 = 'accounts.views.error_404'
handler500 = 'accounts.views.error_500'

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('accounts.urls')),
    path('',            include('tasks.urls')),
    path('api/v1/',     include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
