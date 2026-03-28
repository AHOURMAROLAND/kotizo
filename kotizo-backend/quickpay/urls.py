from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuickPayListView.as_view()),
]
