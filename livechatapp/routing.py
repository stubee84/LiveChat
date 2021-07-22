# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<number>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/chat/general/$', consumers.GeneralChatConsumer.as_asgi()),
    re_path(r'ws/stream/$', consumers.StreamConsumer.as_asgi()),
    re_path(r'ws/.*$', consumers.DefaultUrl.as_asgi())
]