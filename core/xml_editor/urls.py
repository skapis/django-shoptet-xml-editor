from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('receipts/', views.receipts, name='receipts'),
    path('settings/', views.settings, name='settings'),
]