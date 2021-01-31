from django.shortcuts import render
from rest_framework import generics

def index(request):
    return render(request, 'frontend/index.html')


class Login(generics.CreateAPIView):
    def get(request):
        return render(request, 'frontend/login.html')

class Register(generics.GenericAPIView):
    def get(request):
        return render(request, 'frontend/register.html')