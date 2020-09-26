import twilio.rest
import os
import asyncio
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

sid = os.environ.get("TWILIO_ACCOUNT_SID")
token = os.environ.get("TWILIO_AUTH_TOKEN")
phone_number = os.environ.get("TWILIO_NUMBER")

class controller:
    #Rest client variable. Maybe call this rest_clients
    twilio_client: twilio.rest.Client = None
    async def connect(**kwargs):
        try:
            if kwargs['destination'] == "Twilio":
                await controller.twilio_connect(sid=sid,token=token)
        except KeyError:
            return

    #Maybe: put these two functitons into their own twilio child class
    async def twilio_connect(sid: str, token: str):
        if controller.twilio_client is None:
            controller.twilio_client = twilio.rest.Client(username=sid,password=token)
        
    async def twilio_send_message(to_number: str, body: str) -> bool:
        result = controller.twilio_client.messages.create(to=to_number,from_=phone_number,body=body)
        #possibly change this to query the URI for status once it has been sent or received
        if result._properties["status"] == "queued":
            return True
        return False