from django.urls import path
from . import views

urlpatterns = [
    path('register/',        views.register_view,       name='register'),
    path('login/',           views.login_view,           name='login'),
    path('logout/',          views.logout_view,          name='logout'),
    path('profile/',         views.profile_view,         name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('admin/users/',     views.admin_users_view,     name='admin_users'),
    path('admin/audit-logs/',views.audit_logs_view,      name='audit_logs'),
]
