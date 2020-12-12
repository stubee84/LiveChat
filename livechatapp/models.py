from djongo import models

# Create your models here.
class Caller(models.Model):
    _id = models.ObjectIdField()
    number = models.IntegerField(unique=True)
    country = models.CharField(max_length=10)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=10)

class Call(models.Model):
    _id = models.ObjectIdField()
    sid = models.CharField(max_length=50, unique=True)
    length_of_call = models.TimeField()
    caller_id = models.IntegerField()

class Message(models.Model):
    _id = models.ObjectIdField()
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