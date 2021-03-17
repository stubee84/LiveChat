from django.urls import path
from . import views

urlpatterns = [
    path('rooms/', views.index, name='index'),
    path('login/', views.UserLogin.as_view(), name='login'),
    path('register/', views.UserRegistration.as_view(), name='register'),
    path('sms/', views.sms, name='sms'),
    path('voice/', views.voice, name='voice'),
    path('record/', views.record, name='record'),
    path('hangup/', views.hangup, name='hangup'),
    path('menu/', views.menu, name='menu'),
    path('<str:room_name>/', views.room, name='room'),
]