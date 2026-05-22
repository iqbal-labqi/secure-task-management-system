from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'tasks',      views.TaskViewSet,      basename='api-task')
router.register(r'users',      views.UserViewSet,      basename='api-user')
router.register(r'audit-logs', views.AuditLogViewSet,  basename='api-auditlog')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
