import json, base64, sys
from livechatapp.controllers.redis import redisController
from .controllers.utils import database_routines as dr, logger
from .controllers.twilio import twilio_database_routine, twilio_controller as tc
from .controllers.google import google_text_to_speech, google_transcribe_speech
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from .models import Message

class DefaultUrl(WebsocketConsumer):
    def connect(self):
        logger.warning(f"Received connection attempt to URL {self.scope['path']} from {self.scope['client'][0]}")
        self.close()

class GeneralChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "general"
        self.room_group_name = f'chat_general'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"Received connection to URL {self.scope['path']} from {self.scope['client'][0]}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"Closing connection to URL {self.scope['path']} from {self.scope['client'][0]}")

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
        logger.info(f"Received connection to URL {self.scope['path']} from {self.scope['client'][0]}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        if hasattr(ChatConsumer, 'stream_sid'):
            redisController.delete(key=self.room_name)
        logger.info(f"Closing connection to URL {self.scope['path']} from {self.scope['client'][0]}")

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        msg_type = 'C'

        if 'stream' in text_data_json:
            text_to_speech = google_text_to_speech()
            out_bytes, err = await text_to_speech.transcribe_text(text=message)

            #implement some error handling here
            if sys.getsizeof(out_bytes) != 0:
                if not hasattr(ChatConsumer, 'stream_sid'):
                    self.stream_sid = redisController.get(key=self.room_name)
                    logger.info(f"OUTBOUND STREAM SID: {self.stream_sid}")
                await text_to_speech.begin_audio_stream(streamSid=self.stream_sid, in_bytes=out_bytes)
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
                logger.warning("Failed to send message. {}".format(message))
                return

            await twilio_database_routine(number=obj.number.strip('+'), call_sid=obj.call_sid, call_type=msg_type, msg_type=msg_type, message=message)

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
        logger.info(f"Received connection to URL {self.scope['path']} from {self.scope['client'][0]}")
        self.transcribe_speech = google_transcribe_speech()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Closing connection to URL {self.scope['path']} from {self.scope['client'][0]}")
        redisController.delete(key=self.room_group_name)

    async def receive(self, text_data):
        if text_data is None:
            await self.transcribe_speech.end_stream()
            return

        data = json.loads(text_data)
        if data['event'] == "start":
            logger.info(f"Media WS: Received event '{data['event']}': {text_data}")

            call_sid = data['start']['callSid']
            from_number = redisController.get(key=call_sid)
            stream_sid = data['streamSid']
            
            self.room_group_name = stream_sid
            await self.channel_layer.group_add(self.room_group_name,self.channel_name)

            redisController.set(key=from_number, value=stream_sid)
            await self.transcribe_speech.start_transcriptions_stream(call_sid=call_sid)

        elif data['event'] == "media":
            media = data['media']
            chunk = base64.b64decode(media['payload'])

            await self.transcribe_speech.add_req_to_queue(chunk)
        elif data['event'] == "mark":
            logger.info(data)
        elif data['event'] == "stop":
            logger.info(f"Media WS: Received event 'stop': {text_data}")
            logger.info("Stopping...")
            await self.transcribe_speech.end_stream()
        
        if self.transcribe_speech.stream_finished:
            return
        
    async def chat_message(self, event):
        await self.send(text_data=event['message'])

        msg = json.loads(event['message'])
        try:
            mark_num = int(redisController.get(key=msg['streamSid']))
            mark_num += 1
        except:
            mark_num = 1
        redisController.set(key=msg['streamSid'], value=str(mark_num))

        mark = json.dumps({
            "event": "mark",
            "streamSid": msg["streamSid"],
            "mark": {
                "name": f"message {mark_num}"
            }
        })
        await self.send(text_data=mark)