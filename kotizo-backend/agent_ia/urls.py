from django.urls import path
from . import views

urlpatterns = [
    path('', views.ConversationView.as_view()),
    path('effacer/', views.EffacerConversationView.as_view()),
    path('tickets/', views.TicketSupportView.as_view()),
    path('tickets/<int:ticket_id>/', views.TicketDetailView.as_view()),
]