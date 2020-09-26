from django.shortcuts import render
import json, websocket, django.http.request as request
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# Create your views here.
def index(request: request.HttpRequest):
    return render(request, 'index.html')

@csrf_exempt
def sms(request: request.HttpRequest):
    text = request.POST.get("Body")
    from_number = request.POST.get("From")

    text = text.split(":")
    message: dict = dict()
    try:
        room_name = text[0].strip(' ')
        message = {"message":from_number + ': ' + text[1].strip(' ')}

        #Create a generalized function for this which allows for injection to different sources. i.e. a remote source that requires authentication
        ws = websocket.WebSocket()
        ws.connect(f"ws://localhost/ws/chat/{room_name.lower()}/")
        ws.send(json.dumps(message))
        ws.close()
        message["Success"] = True
    except IndexError as e:
        message = {"Error":"incorrect message format"}
    
    return HttpResponse(json.dumps(message))

def room(request: request.HttpRequest, room_name):
    return render(request, 'room.html', {
        'room_name': room_name
    })