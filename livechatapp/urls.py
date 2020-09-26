from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sms/', views.sms, name='sms'),
    path('<str:room_name>/', views.room, name='room'),
]