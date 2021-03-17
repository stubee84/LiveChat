from django.urls import path
from . import views


urlpatterns = [
    path('', views.Dashboard.as_view(), name='live-chat'),
    path('chat/', views.Dashboard.as_view(), name='live-chat'),
    path('login/', views.Login.as_view(), name='frontend-login'),
    path('register/', views.Register.as_view(), name='frontend-register')
]