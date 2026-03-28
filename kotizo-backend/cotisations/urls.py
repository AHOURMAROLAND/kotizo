from django.urls import path
from . import views

urlpatterns = [
    path('', views.CotisationListView.as_view()),
]
