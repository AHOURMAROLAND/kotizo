"""Kotizo URL Configuration"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/cotisations/', include('cotisations.urls')),
    path('api/paiements/', include('paiements.urls')),
    path('api/quickpay/', include('quickpay.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/agent/', include('agent_ia.urls')),
    path('api/admin/', include('admin_panel.urls')),
]
