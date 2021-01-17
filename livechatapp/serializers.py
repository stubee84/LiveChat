import models
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        models = models.User
        fields = ['_id','email','password','temporary','session_token']

class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Call
        fields = ['_id','sid','length_of_call','caller_id']

class CallerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Caller
        fields = ['_id','number','country','city','state']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = ['_id','call_id','message_type','message']