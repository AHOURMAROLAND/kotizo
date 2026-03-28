from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminLogListView.as_view()),
]
