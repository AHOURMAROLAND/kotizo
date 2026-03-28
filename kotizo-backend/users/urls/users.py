from django.urls import path
from users.views.users import (
    MonProfilView,
    ThemeView,
    ProfilPublicView,
    VerificationIdentiteView,
    SessionsActivesView,
    RevoquerSessionView,
    DemandeBusinessView,
    ReclamationView,
    StatsUserView,
    StatsFinancieresView,
    ParrainageStatsView,
    SupprimerCompteView,
)

urlpatterns = [
    path('moi/', MonProfilView.as_view(), name='mon-profil'),
    path('moi/theme/', ThemeView.as_view(), name='theme'),
    path('moi/supprimer/', SupprimerCompteView.as_view(), name='supprimer-compte'),
    path('profil-public/<uuid:user_id>/', ProfilPublicView.as_view(), name='profil-public'),
    path('verification/soumettre/', VerificationIdentiteView.as_view(), name='verification-identite'),
    path('sessions/', SessionsActivesView.as_view(), name='sessions-actives'),
    path('sessions/<int:session_id>/', RevoquerSessionView.as_view(), name='revoquer-session'),
    path('demande-business/', DemandeBusinessView.as_view(), name='demande-business'),
    path('reclamations/', ReclamationView.as_view(), name='reclamations'),
    path('stats/', StatsUserView.as_view(), name='stats-user'),
    path('stats/financieres/', StatsFinancieresView.as_view(), name='stats-financieres'),
    path('parrainage/stats/', ParrainageStatsView.as_view(), name='parrainage-stats'),
]
