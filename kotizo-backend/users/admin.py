from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SessionDevice, VerificationObligatoire


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['pseudo', 'email', 'niveau', 'statut', 'identite_verifiee', 'date_inscription']
    list_filter = ['niveau', 'statut', 'identite_verifiee']
    search_fields = ['pseudo', 'email', 'telephone']
    ordering = ['-date_inscription']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Infos', {'fields': ('pseudo', 'nom', 'prenom', 'telephone', 'whatsapp_numero', 'date_naissance')}),
        ('Statut', {'fields': ('niveau', 'statut', 'identite_verifiee', 'statut_verification')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'admin_role')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'pseudo', 'nom', 'prenom', 'password1', 'password2'),
        }),
    )


@admin.register(SessionDevice)
class SessionDeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_name', 'is_active', 'date_connexion']


@admin.register(VerificationObligatoire)
class VerificationObligatoireAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_limite', 'compte_ferme']
