from django.urls import path
from users.views.auth import (
    InscriptionView,
    ConnexionView,
    VerificationEmailView,
    VerificationWhatsAppView,
    MotDePasseOublieView,
    ChangerMotDePasseView,
    ConfirmerActionView,
    VerifierCNIConnexionView,
    DeconnexionView,
)

urlpatterns = [
    path('inscription/', InscriptionView.as_view(), name='inscription'),
    path('connexion/', ConnexionView.as_view(), name='connexion'),
    path('deconnexion/', DeconnexionView.as_view(), name='deconnexion'),
    path('verification-email/', VerificationEmailView.as_view(), name='verification-email'),
    path('verification-wa/', VerificationWhatsAppView.as_view(), name='verification-wa'),
    path('mot-de-passe-oublie/', MotDePasseOublieView.as_view(), name='mdp-oublie'),
    path('changer-mot-de-passe/', ChangerMotDePasseView.as_view(), name='changer-mdp'),
    path('confirmer-action/', ConfirmerActionView.as_view(), name='confirmer-action'),
    path('verifier-cni/', VerifierCNIConnexionView.as_view(), name='verifier-cni'),
]
