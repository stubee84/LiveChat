from django.shortcuts import render
from rest_framework import generics, request
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

class Login(generics.CreateAPIView):
    def get(request: HttpRequest , drf: request.Request):
        return render(drf, 'frontend/login.html')

class Register(generics.GenericAPIView):
    def get(request: HttpRequest, drf: request.Request):
        return render(drf, 'frontend/register.html')

@method_decorator(login_required, name="get")
class Dashboard(generics.GenericAPIView):
    def get(request: HttpRequest, drf: request.Request):
        return render(drf, 'frontend/index.html')