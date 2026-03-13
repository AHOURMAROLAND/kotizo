from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationsView.as_view()),
    path('non-lues/', views.NombreNonLuesView.as_view()),
    path('tout-lire/', views.MarquerToutesLuesView.as_view()),
    path('<int:notification_id>/lire/', views.MarquerLueView.as_view()),
]