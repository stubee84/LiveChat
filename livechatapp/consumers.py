# chat/consumers.py
import json, re
from .controllers.main import twilio_controller
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer

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
            print("could not match regular expression")

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

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

class StreamConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)
        # message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': text_data
        }))