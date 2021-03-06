import django.http.request as request
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from ..models import User

class CustomAuth(BaseBackend):
    def authenticate(self, request: request.HttpRequest = None, username: str = None, password: str = None):
        try:
            login: User = self.get_user(email=username)
        except User.DoesNotExist:
            return None

        pwd_valid: bool = check_password(password=password, encoded=login.password)
        if pwd_valid:
            return login

        return None
    
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    def get_user(self, email: str):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise User.DoesNotExist