from django.urls import path, re_path
from livechatapp.views.views import *
from livechatapp.views.twilio_views import *

urlpatterns = [
    path('rooms/', index, name='index'),
    path('login/', UserLogin.as_view(), name='login'),
    path('register/', UserRegistration.as_view(), name='register'),
    re_path('numbers/$', GetNumbers.as_view(), name='numbers'),
    re_path('numbers/(?P<number>\d{11})/$', GetNumbers.as_view(), name='numbers'),
    re_path('^messages/(?P<number>\d{11})/$', GetMessages.as_view(), name='messages'),
    path('sms/', sms, name='sms'),
    path('voice/', voice, name='voice'),
    path('record/', record, name='record'),
    path('hangup/', hangup, name='hangup'),
    path('menu/', menu, name='menu'),
    # path('<str:room_name>/', room, name='room'),
]