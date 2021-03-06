# from django.db.models import Q
from django.contrib.auth import authenticate
from . import models
from .controllers.main import password_management
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=models.User.objects.all())])
    password = serializers.CharField(min_length=8, write_only=True)

    def create(self, validated_data: dict):
        return models.User.objects.create(email=validated_data['email'], password=password_management(password=validated_data['password']).hash())

    class Meta:
        model = models.User
        fields = ['active','email','password','temporary','session_token']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'email']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data: dict):
        user: models.User = authenticate(username=data['email'], password=data['password'])
        if user and user.active:
            return user
        raise serializers.ValidationError("could not validate provided credentials")
        # return models.User.objects.get(Q(email=data['email']),Q(password=password_management.hash(data['password'])))

class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Call
        fields = ['sid','length_of_call','caller_id']

class CallerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Caller
        fields = ['number','country','city','state']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = ['call_id','message_type','message']