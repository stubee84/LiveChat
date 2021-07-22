from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField(default=True, null=False)
    email = models.CharField(max_length=30, unique=True, null=False, blank=False)
    password = models.CharField(max_length=30, null=False, blank=False)
    temporary = models.BooleanField(default=False, null=False)
    last_login = models.DateTimeField(max_length=30, null=False, auto_now=True)
    session_token = models.CharField(max_length=100, null=True)

    def is_authenticated(self):
        return True

class Caller(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.CharField(max_length=15, unique=True)
    country = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=10)

class Call(models.Model):
    id = models.AutoField(primary_key=True)
    sid = models.CharField(max_length=50, unique=True)
    length_of_call = models.IntegerField()
    caller_id = models.IntegerField()
    CALL_TYPES = (
        ('S', 'SMS'),
        ('R', 'Recording'),
        ('L', 'Live'),
    )
    call_type = models.CharField(max_length=1, choices=CALL_TYPES)

class Message(models.Model):
    id = models.AutoField(primary_key=True)
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