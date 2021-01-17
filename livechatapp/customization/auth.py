import django.http.request as request
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from ..models import User

class CustomAuth(BaseBackend):
    def authenticate(self, request: request.HttpRequest, username: str = None, password: str = None):
        try:
            login = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        pwd_valid = check_password(password, login.password)
        if pwd_valid:
            return login_valid

        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(_id=user_id)
        except User.DoesNotExist:
            return None