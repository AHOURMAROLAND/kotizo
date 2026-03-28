from django.contrib import admin
from .models import Cotisation, Participation, Commentaire, NotationCreateur


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'createur', 'statut', 'progression', 'date_creation']
    list_filter = ['statut', 'supprime']
    search_fields = ['nom', 'slug', 'createur__pseudo']


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ['participant', 'cotisation', 'montant', 'statut', 'rang_paiement']
    list_filter = ['statut']


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['auteur', 'cotisation', 'date_creation']


@admin.register(NotationCreateur)
class NotationCreateurAdmin(admin.ModelAdmin):
    list_display = ['noteur', 'cotisation', 'note', 'date_creation']
