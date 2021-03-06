# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<number>\d+)/$', consumers.ChatConsumer),
    re_path(r'ws/chat/general/$', consumers.GeneralChatConsumer),
    re_path(r'ws/stream/$', consumers.StreamConsumer),
    re_path(r'ws/.*$', consumers.DefaultUrl)
]