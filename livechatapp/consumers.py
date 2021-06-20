import json, base64, sys
from .controllers.main import twilio_controller as tc, google_transcribe_speech, google_text_to_speech, database_routines as dr
from .controllers.twilio import twilio_database_routine
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .models import Message

class DefaultUrl(WebsocketConsumer):
    def connect(self):
        print(f"Received connection to URL {self.scope['path']} from {self.scope['client'][0]}")
        self.close()

class GeneralChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "general"
        self.room_group_name = f'chat_general'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await dr.insert(model=Message, message=message, message_type="C")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
        
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event['message']))

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['number']
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
        msg_type = 'C'

        if 'stream' in text_data_json:
            text_to_speech = google_text_to_speech()
            out_bytes = await text_to_speech.transcribe_text(text=message)

            #implement some error handling here
            if sys.getsizeof(out_bytes) != 0:
                await text_to_speech.begin_audio_stream(streamSid=text_data_json['stream'], in_bytes=out_bytes)
        else:
            if 'sms' in text_data_json:
                callable = tc.twilio_send_message
                msg_type = 'S'
            elif 'call' in text_data_json:
                callable = tc.twilio_call_with_recording
                msg_type = 'O'
    
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
            obj = await callable(to_number=self.room_name, body=message)
            if obj is None:
                print("Failed to send message. {}".format(message))
                return


            await twilio_database_routine(number=obj.number.strip('+'), call_sid=obj.call_sid, msg_type=msg_type, message=message)

        # matches = num_reg.match(message)
        # if matches is not None:
        #     try:
        #         to_number = matches.groups()[0]
        #         text = str(message).split(':')
        #         method = text[0]
        #         message = text[len(text)-1].strip()
            
        #         tc = twilio_controller()
        #         await tc.connect(destination="Twilio")
                
        #         if method == "text":
        #             result = await tc.twilio_send_message(to_number=to_number,body=message)
        #         else:
        #             result = await tc.twilio_call_with_recording(to_number=to_number,body=message)

        #         if result == False:
        #             message = "Failed to send message. {}".format(message)
        #     except IndexError as e:
        #         message = "Failed to send message. {}".format(e)
        # else:
        #     text_to_speech = google_text_to_speech()
        #     out_bytes = await text_to_speech.transcribe_text(text=message)

        #     #implement some error handling here
        #     if sys.getsizeof(out_bytes) != 0:
        #         await text_to_speech.begin_audio_stream(streamSid=stream_sid, in_bytes=out_bytes)

        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': message
        #     }
        # )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        
        try:
            text = json.dumps({
                'message': message,
                'stream': event['stream']
            })
        except KeyError:
            text = message

        # Send message to WebSocket
        await self.send(text_data=json.dumps(text))

class StreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.transcribe_speech = google_transcribe_speech()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if text_data is None:
            await self.transcribe_speech.end_stream()
            return

        data = json.loads(text_data)
        if data['event'] == "start":
            print(f"Media WS: Received event '{data['event']}': {text_data}")
            await self.channel_layer.group_add(data["streamSid"],self.channel_name)
            await self.transcribe_speech.start_transcriptions_stream(call_sid=data["start"]["callSid"])

        elif data['event'] == "media":
            media = data['media']
            chunk = base64.b64decode(media['payload'])

            await self.transcribe_speech.add_req_to_queue(chunk)
        elif data['event'] == "mark":
            print(data)
        elif data['event'] == "stop":
            print(f"Media WS: Received event 'stop': {text_data}")
            print("Stopping...")
            await self.transcribe_speech.end_stream()
        
        if self.transcribe_speech.stream_finished:
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