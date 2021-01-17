from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('sms/', views.sms, name='sms'),
    path('voice/', views.voice, name='voice'),
    path('record/', views.record, name='record'),
    path('hangup/', views.hangup, name='hangup'),
    path('menu/', views.menu, name='menu'),
    path('<str:room_name>/', views.room, name='room'),
]