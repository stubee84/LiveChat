# chat/consumers.py
import json, re, base64
from django.utils.functional import LazyObject
from .controllers.main import twilio_controller, google_transcribe_speech, google_text_to_speech
from channels.generic.websocket import AsyncWebsocketConsumer

 #+14074910011 or 14074910011 or 4074910011
num_reg = re.compile(r'.*:(\d{10}|\d{11}|(\+\d{11})):.*')

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        matches = num_reg.match(message)
        if matches is not None:
            try:
                to_number = matches.groups()[0]
                text = str(message).split(':')
                method = text[0]
                message = text[len(text)-1].strip()
            
                await twilio_controller.connect(destination="Twilio")
                
                if method == "text":
                    result = await twilio_controller.twilio_send_message(to_number=to_number,body=message)
                else:
                    result = await twilio_controller.twilio_call_with_recording(to_number=to_number,body=message)

                if result == False:
                    message = "Failed to send message. {}".format(message)
            except IndexError as e:
                message = "Failed to send message. {}".format(e)
        else:
            text = str(message).split(':')
            method = text[0]
            stream_sid = text[1]
            message = text[len(text)-1].strip()

            text_to_speech = google_text_to_speech()
            filename = await text_to_speech.transcribe_text(text=message)
            await text_to_speech.begin_audio_stream(streamSid=stream_sid, filename=filename)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        
        try:
            stream = event['stream']
            text = json.dumps({
                'message': message,
                'stream': stream
            })
        except KeyError:
            text = json.dumps({
                'message': message
            })

        # Send message to WebSocket
        await self.send(text_data=text)

class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # await twilio_controller.connect(destination="twilio")
        await google_transcribe_speech.start_transcriptions_stream()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if text_data is None:
            await google_transcribe_speech.end_stream()
            return

        data = json.loads(text_data)
        if data['event'] == "start":
            print(f"Media WS: Received event '{data['event']}': {text_data}")
            await self.channel_layer.group_add(
                data["streamSid"],
                self.channel_name
            )

            await self.channel_layer.group_send(
                "chat_lobby",
                {
                    'type': 'chat_message',
                    'message': f'Incoming stream from {data["streamSid"]}'
                }
            )
        elif data['event'] == "media":
            media = data['media']
            chunk = base64.b64decode(media['payload'])

            await google_transcribe_speech.add_req_to_queue(chunk)
        elif data['event'] == "mark":
            print(data)
        elif data['event'] == "stop":
            print(f"Media WS: Received event 'stop': {text_data}")
            print("Stopping...")
            await google_transcribe_speech.end_stream()
        
        if google_transcribe_speech.stream_finished:
            return
        
    async def chat_message(self, event):
        await self.send(text_data=event['message'])

        msg = json.loads(event['message'])
        mark = json.dumps({
            "event": "mark",
            "streamSid": msg["streamSid"],
            "mark": {
                "name": "message 1"
            }
        })
        await self.send(text_data=mark)