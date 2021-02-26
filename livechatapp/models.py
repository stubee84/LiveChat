from djongo import models

class User(models.Model):
    id = models.ObjectIdField()
    email = models.CharField(max_length=30, unique=True, null=False, blank=False)
    password = models.CharField(max_length=30, null=False, blank=False)
    temporary = models.BooleanField(default=False, null=False)
    session_token = models.CharField(max_length=100, null=True)

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
    MESSAGE_TYPES = (
        ('S', 'SMS'),
        ('R', 'Inbound Recorded Call'),
        ('O', 'Outbound Text Call'),
        ('LI', 'Live inbound transcription'),
        ('LO', 'Live outbound text to speech'),
    )
    message_type = models.CharField(max_length=2, choices=MESSAGE_TYPES)
    message = models.TextField()