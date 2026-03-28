from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaiementListView.as_view()),
]
