from django.shortcuts import render
import json, websocket, asyncio, channels.layers, django.http.request as request
from asgiref.sync import async_to_sync
from .consumers import ChatConsumer
from .controllers import main
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from twilio.request_validator import RequestValidator

# Create your views here.
def index(request: request.HttpRequest):
    return render(request, 'index.html')

#TODO: update to send using asgiref.sync.async_to_sync instead of websocket client
@csrf_exempt
def sms(request: request.HttpRequest):
    text = request.POST.get("Body")
    from_number = request.POST.get("From")

    text = text.split(":")
    message: dict = dict()
    try:
        room_name = text[0].strip(' ')
        message = {"message":from_number + ': ' + text[1].strip(' ')}

        #TODO: Create a generalized function for this which allows for injection to different sources. i.e. a remote source that requires authentication
        ws = websocket.WebSocket()
        ws.connect(f"ws://localhost/ws/chat/{room_name.lower()}/")
        ws.send(json.dumps(message))
        ws.close()
        message["Success"] = True
    except IndexError as e:
        message = {"Error":"incorrect message format"}
    
    return HttpResponse(json.dumps(message))

@csrf_exempt
#TODO: configure Twilio security using the Twilio signature
#TODO: configure a 404 not found or rejected HttpResponse on error
def voice(request: request.HttpRequest):
    try:
        twilio_signature = request.META['HTTP_X_TWILIO_SIGNATURE']
        resp = VoiceResponse()
        with resp.gather(num_digits=1, action="/chat/menu/", method="POST", timeout=3) as gather:
            gather.say(message="Press 1 to record a message or press 2 stream the voice call.", loop=1)
    
        return HttpResponse(str(resp))
    except KeyError:
        return

@csrf_exempt
def menu(request: request.HttpRequest):
    try:
        twilio_signature = request.META['HTTP_X_TWILIO_SIGNATURE']
        digit = request.POST.get('Digits')

        resp = VoiceResponse()
        #record
        if digit == '1':
            resp.say("Please leave a message. Press the pound or hash key to end the recording.")
            #without an action or recording_status_callbath attribute then you will have an endless loop of calling into the view
            resp.record(play_beep=True, max_length=30, finish_on_key="#", recording_status_callback="/chat/record/", action="/chat/hangup/")

            channel_layer = channels.layers.get_channel_layer()
            async_to_sync(channel_layer.group_send)("chat_lobby", {
                "type": "chat_message",
                "message": 'Incoming recording...'
            })
        elif digit == '2':
            resp.say("Please begin speaking...")
            connect = Connect()
            connect.stream(url=main.ws_url)
            resp.append(connect)
        else:
            resp.say("Incorrect entry. Please try again.")
            resp.redirect('/chat/voice/')
        
        return HttpResponse(str(resp))
    except KeyError:
        return
            

@csrf_exempt
#TODO: configure the recording as an asynchronous thread
def record(request: request.HttpRequest):
    try:
        twilio_signature = request.META['HTTP_X_TWILIO_SIGNATURE']
        call_sid = request.POST.get("CallSid")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main.twilio_controller.connect(destination="twilio"))
        caller = loop.run_until_complete(main.twilio_controller.get_call_info(call_sid=call_sid))

        transcript = main.google_controller.download_audio_and_transcribe(recording_url=request.POST.get("RecordingUrl"))
        print(transcript)
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)("chat_lobby", {
            "type": "chat_message",
            "message": f'{caller} - {transcript}'
        })
        
        # gcs_uri = main.google_controller.download_audio_and_upload(recording_sid=request.POST.get("RecordingSid"), recording_url=request.POST.get("RecordingUrl"))
        # transcript = main.google_controller.transcribe_audio(gcs_uri=gcs_uri)
        return HttpResponse()
    except KeyError:
        return

@csrf_exempt
def hangup(request: request.HttpRequest):
    try:
        twilio_signature = request.META['HTTP_X_TWILIO_SIGNATURE']
        resp = VoiceResponse()
        resp.hangup()

        return HttpResponse(str(resp))
    except KeyError:
        return

def room(request: request.HttpRequest, room_name):
    return render(request, 'room.html', {
        'room_name': room_name
    })