from twilio.twiml.voice_response import VoiceResponse, Connect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from livechatapp.controllers.redis import redisController
from livechatapp.controllers.google import google_transcribe_speech
from livechatapp.controllers.utils import ws_url
from livechatapp.controllers.twilio import twilio_database_routine, twilio_controller as tc
from livechatapp.models import Call, Caller
from asgiref.sync import async_to_sync
import json, asyncio, channels.layers, django.http.request as request

@csrf_exempt
def sms(request: request.HttpRequest):
    text = request.POST.get("Body")
    from_number = request.POST.get("From").strip('+')
    sid = request.POST.get("MessageSid")

    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(f"chat_{from_number}", {"type": "chat_message", "message": text})

    async_to_sync(twilio_database_routine)(number=from_number, call_sid=sid, call_type='S', msg_type='S', message=text)

    return HttpResponse(json.dumps({"Success": True}))

@csrf_exempt
#TODO: configure Twilio security using the Twilio signature
#TODO: configure a 404 not found or rejected HttpResponse on error
def voice(request: request.HttpRequest):
    try:
        _ = request.META['HTTP_X_TWILIO_SIGNATURE']
        resp = VoiceResponse()
        with resp.gather(num_digits=1, action="/api/menu/", method="POST", timeout=3) as gather:
            gather.say(message="Press 1 to record a message or press 2 stream the voice call.", loop=1)
    
        return HttpResponse(str(resp))
    except KeyError:
        return

@csrf_exempt
def menu(request: request.HttpRequest):
    try:
        _ = request.META['HTTP_X_TWILIO_SIGNATURE']
        digit = request.POST.get('Digits')
        from_number = request.POST.get("From").strip("+")
        call_sid = request.POST.get("CallSid")

        channel_layer = channels.layers.get_channel_layer()
        resp = VoiceResponse()
        #record
        if digit == '1':
            resp.say("Please leave a message. Press the pound or hash key to end the recording.")
            #without an action or recording_status_callback attribute then you will have an endless loop of calling into the view
            resp.record(play_beep=True, max_length=30, finish_on_key="#", recording_status_callback="/api/record/", action="/api/hangup/")

            async_to_sync(channel_layer.group_send)(f"chat_{from_number}", {"type": "chat_message", "message": 'Incoming recording...'}) 
        #stream
        elif digit == '2':
            caller: Caller = Caller.objects.get(number=from_number)
            Call(sid=call_sid, length_of_call=0, caller_id=caller.id, call_type="L").save()
            redisController.set(key=call_sid,value=from_number)

            async_to_sync(channel_layer.group_send)(f"chat_{from_number}", {"type": "chat_message", "stream": True, "message": 'Incoming stream...'})

            resp.say("Please begin speaking...")
            connect = Connect()
            connect.stream(url=ws_url)
            resp.append(connect)
        else:
            resp.say("Incorrect entry. Please try again.")
            resp.redirect('/api/voice/')
        
        return HttpResponse(str(resp))
    except KeyError:
        return
            

@csrf_exempt
def record(request: request.HttpRequest):
    try:
        _ = request.META['HTTP_X_TWILIO_SIGNATURE']
        call_sid = request.POST.get("CallSid")

        from_number = tc.get_call_info(sid=call_sid).from_
        transcribe_speech = google_transcribe_speech()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(transcribe_speech.connect(destination="speech"))
        transcript = transcribe_speech.download_audio_and_transcribe(recording_url=request.POST.get("RecordingUrl"))
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"chat_{from_number.strip('+')}", {"type": "chat_message","message": transcript})

        async_to_sync(twilio_database_routine)(number=from_number.strip('+'), call_sid=call_sid, call_type='R', msg_type='R', message=transcript)
        return HttpResponse()
    except KeyError:
        return

@csrf_exempt
def hangup(request: request.HttpRequest):
    try:
        _ = request.META['HTTP_X_TWILIO_SIGNATURE']
        resp = VoiceResponse()
        resp.hangup()

        return HttpResponse(str(resp))
    except KeyError:
        return

# @decorators.login_required
# def room(request: request.HttpRequest, room_name):
#     return render(request, 'room.html', {
#         'room_name': room_name
#     })