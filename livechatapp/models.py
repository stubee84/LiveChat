from djongo import models
from datetime import datetime

class User(models.Model):
    id = models.ObjectIdField()
    is_active = models.BooleanField(default=True, null=False)
    email = models.CharField(max_length=30, unique=True, null=False, blank=False)
    password = models.CharField(max_length=30, null=False, blank=False)
    temporary = models.BooleanField(default=False, null=False)
    last_login = models.DateTimeField(max_length=30, null=False, auto_now=True)
    session_token = models.CharField(max_length=100, null=True)

    def is_authenticated(self):
        return True

class Caller(models.Model):
    id = models.ObjectIdField()
    number = models.IntegerField(unique=True)
    country = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=10)

class Call(models.Model):
    id = models.ObjectIdField()
    sid = models.CharField(max_length=50, unique=True)
    length_of_call = models.TimeField()
    caller_id = models.IntegerField()

class Message(models.Model):
    id = models.ObjectIdField()
    call_id = models.IntegerField()
    number = models.IntegerField()
    MESSAGE_TYPES = (
        ('C', 'Chat'),
        ('S', 'SMS'),
        ('R', 'Inbound Recorded Call'),
        ('O', 'Outbound Text Call'),
        ('LI', 'Live inbound transcription'),
        ('LO', 'Live outbound text to speech'),
    )
    message_type = models.CharField(max_length=2, choices=MESSAGE_TYPES)
    message = models.TextField()