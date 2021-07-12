# from django.db.models import Q
from django.contrib.auth import authenticate
from .models import User, Call, Caller, Message
from .controllers.main import password_management
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(
        queryset=User.objects.all(),
        message="NOT UNIQUE: email is already in use"
        )])
    password = serializers.CharField(min_length=9, write_only=True)

    def create(self, validated_data: dict):
        user = None
        try:
            user = User.objects.create(email=validated_data['email'], password=password_management(password=validated_data['password']).hash())
        except exceptions.ValidationError as e:
            raise exceptions.ValidationError(detail=e.detail, code=e.status_code)
        return user

    class Meta:
        model = User
        fields = ['is_active','email','password','temporary','session_token']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data: dict):
        user: User = authenticate(username=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("could not validate provided credentials")

class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ['sid','length_of_call','caller_id']

class CallerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caller
        fields = ['number','country']

class NumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caller
        fields = ['number']
        extra_kwargs = {
            'number': {'validators': []},
        }

class MessageSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField()
    call_id = serializers.IntegerField()
    message_type = serializers.ChoiceField(choices=('C','S','R','O','LI','LO'), required=True)
    message = serializers.CharField(required=True)

    def create(self, validated_data: dict):
        Message.objects.create(**validated_data)

    class Meta:
        model = Message
        fields = ['call_id','number','message_type','message']