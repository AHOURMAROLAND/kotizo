from django.urls import path
from . import views

urlpatterns = [
    path('initier/<str:slug>/', views.InitierPaiementCotisationView.as_view()),
    path('webhook/payin/', views.WebhookPayinView.as_view()),
    path('webhook/payout/', views.WebhookPayoutView.as_view()),
    path('historique/', views.HistoriqueTransactionsView.as_view()),
    path('remboursement/', views.DemandeRemboursementView.as_view()),
]