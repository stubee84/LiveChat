from . import models
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=models.User.objects.all())])
    password = serializers.CharField(min_length=8, write_only=True)

    def create(self, validated_data: dict):
        return models.User.objects.create(email=validated_data['email'], password=validated_data['password'])
    class Meta:
        model = models.User
        fields = ['email','password','temporary','session_token']

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