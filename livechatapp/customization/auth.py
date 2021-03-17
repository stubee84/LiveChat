import django.http.request as request
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from ..models import User

class CustomAuth(BaseBackend):
    def authenticate(self, request: request.HttpRequest = None, username: str = None, password: str = None) -> User:
        try:
            login: User = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        pwd_valid: bool = check_password(password=password, encoded=login.password)
        if pwd_valid:
            return login

        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise User.DoesNotExist