from django.shortcuts import render
from rest_framework import generics, request
from django.http.request import HttpRequest

class Login(generics.CreateAPIView):
    def get(request: HttpRequest , drf: request.Request):
        return render(drf, 'frontend/login.html')

    def post(request: HttpRequest, drf: request.Request):
        pass

class Register(generics.GenericAPIView):
    def get(request: HttpRequest, drf: request.Request):
        return render(drf, 'frontend/register.html')