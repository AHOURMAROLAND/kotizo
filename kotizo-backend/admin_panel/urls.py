from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view()),
    path('users/', views.AdminUsersView.as_view()),
    path('users/<uuid:user_id>/', views.AdminUserDetailView.as_view()),
    path('verifications/', views.AdminVerificationsView.as_view()),
    path('verifications/<int:verif_id>/action/', views.AdminVerificationActionView.as_view()),
    path('transactions/', views.AdminTransactionsView.as_view()),
    path('alertes/', views.AdminAlertesView.as_view()),
    path('sanctions/', views.AdminSanctionView.as_view()),
    path('tickets/', views.AdminTicketsView.as_view()),
    path('tickets/<int:ticket_id>/', views.AdminTicketActionView.as_view()),
]