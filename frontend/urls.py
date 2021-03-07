from django.urls import path
from . import views


urlpatterns = [
    path('', views.Login.as_view(), name='frontend-login'),
    path('login/', views.Login.as_view(), name='frontend-login'),
    path('register/', views.Login.as_view(), name='frontend-register')
]