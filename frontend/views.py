from django.http import response
from django.shortcuts import render
from rest_framework import generics, request, response, status
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

class Login(generics.CreateAPIView):
    def get(request: HttpRequest, drf: request.Request):
        return render(drf, 'frontend/login.html')

@method_decorator(csrf_protect, name="get")
@method_decorator(login_required, name="get")
class Logout(generics.GenericAPIView):
    def get(self, drf: request.Request):
        logout(request=drf)
        return render(drf, 'frontend/login.html')

class Register(generics.GenericAPIView):
    def get(request: HttpRequest, drf: request.Request):
        return render(drf, 'frontend/register.html')

@method_decorator(login_required, name="get")
class Dashboard(generics.GenericAPIView):
    def get(request: HttpRequest, drf: request.Request):
        return render(drf, 'frontend/index.html')