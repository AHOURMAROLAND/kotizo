from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuickPayCreateView.as_view()),
    path('<str:code>/', views.QuickPayDetailView.as_view()),
    path('<str:code>/payer/', views.InitierPaiementQuickPayView.as_view()),
    path('webhook/', views.WebhookQuickPayView.as_view()),
]