from django.urls import path
from .views import *

urlpatterns = [
    path('rooms/', index, name='index'),
    path('login/', UserLogin.as_view(), name='login'),
    path('register/', UserRegistration.as_view(), name='register'),
    path('numbers/', GetNumbers.as_view(), name='numbers'),
    path('sms/', sms, name='sms'),
    path('voice/', voice, name='voice'),
    path('record/', record, name='record'),
    path('hangup/', hangup, name='hangup'),
    path('menu/', menu, name='menu'),
    path('<str:room_name>/', room, name='room'),
]