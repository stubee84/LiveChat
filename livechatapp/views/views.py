import json, websocket, asyncio, channels.layers, django.http.request as request
from rest_framework import response, status, views, generics
from ..models import *
from ..serializers import *
from django.shortcuts import render
from asgiref.sync import async_to_sync
from ..consumers import ChatConsumer
from ..controllers import main
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from twilio.request_validator import RequestValidator

class UserRegistration(views.APIView):
    def post(self, request: request.HttpRequest, format='json') -> response.Response:
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user: User = serializer.create(validated_data=request.data)
            if user:
                return response.Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_protect, name="post")
class UserLogin(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request: request.HttpRequest, format='json') -> response.Response:
        serializer: LoginSerializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data

            if user is not None:
                login(request=request, user=user)
                return response.Response(data={
                    "user": UserSerializer(user, context=self.get_serializer_context()).data
                    }, status=status.HTTP_201_CREATED)
            else:
                print(f'failed to login user: {user}')
        except BaseException as err:
            print(f'error: {err}')
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

@method_decorator(login_required, name="get")
@method_decorator(csrf_protect, name="get")
class GetNumbers(generics.ListAPIView):
    queryset = Caller.objects.values('number')
    serializer_class: NumberSerializer = NumberSerializer

@method_decorator(login_required, name="get")
@method_decorator(csrf_protect, name="get")
class GetMessages(generics.ListAPIView):
    serializer_class: MessageSerializer = MessageSerializer

    def get_queryset(self):
        num = self.kwargs['number']
        return Message.objects.filter(number=num)

@login_required
def index(request: request.HttpRequest):
    return render(request, 'index.html')

#TODO: update to send using asgiref.sync.async_to_sync instead of websocket client
@csrf_exempt
def sms(request: request.HttpRequest):
    text = request.POST.get("Body")
    from_number = request.POST.get("From")

    # text = text.split(":")
    message: dict = dict()
    try:
        # room_name = text[0].strip(' ')
        message = {"message":text}
        # message['sms'] = True
        from_number = from_number.strip('+')
        caller = Caller.objects.get(number=from_number)
        if caller is None:
            caller = Caller(
            number=from_number, 
            country=request.POST.get("FromCountry"),
            city=request.POST.get("FromCity"),
            state=request.POST.get("FromState")).save()

        # caller = Caller.objects.get(number=from_number)
        sid = request.POST.get("MessageSid")
        Call(sid=sid,length_of_call=0,caller_id=caller.id).save()
        call = Call.objects.get(sid=sid)

        #TODO: Create a generalized function for this which allows for injection to different sources. i.e. a remote source that requires authentication
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"chat_{from_number}", {"type": "chat_message", "message": message})
        # ws = websocket.WebSocket()
        # ws.connect(f"ws://localhost/ws/chat/{from_number}/")
        # ws.send(json.dumps(message))
        # ws.close()
        message["Success"] = True
    except BaseException as e:
        print(e)
        message = {"Error":e}
    
    msg = Message(call_id=call.id,number=from_number,message_type="S",message=message['message']).save()

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
        
        tc = main.twilio_controller()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tc.connect(destination="twilio"))
        caller = loop.run_until_complete(tc.get_call_info(call_sid=call_sid).from_formatted)

        transcribe_speech = main.google_transcribe_speech()
        transcript = transcribe_speech.download_audio_and_transcribe(recording_url=request.POST.get("RecordingUrl"))
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)("chat_lobby", {
            "type": "chat_message",
            "message": f'{caller} - {transcript}'
        })
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

@login_required
def room(request: request.HttpRequest, room_name):
    return render(request, 'room.html', {
        'room_name': room_name
    })