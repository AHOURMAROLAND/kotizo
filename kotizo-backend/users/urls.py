from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('inscription/', views.InscriptionView.as_view()),
    path('connexion/', views.ConnexionView.as_view()),
    path('deconnexion/', views.DeconnexionView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('verifier-email/<str:token>/', views.VerifierEmailView.as_view()),
    path('moi/', views.MoiView.as_view()),
    path('fcm-token/', views.FCMTokenView.as_view()),
]