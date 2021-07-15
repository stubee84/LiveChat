from livechatapp.models import Caller, Call, Message
from channels.db import database_sync_to_async
import twilio.rest, os
from dotenv import load_dotenv
from .utils import logger

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

class twilio_controller:
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    phone_number = os.environ.get("TWILIO_NUMBER")
    twilio_client: twilio.rest.Client = twilio.rest.Client(username=sid,password=token)
    call_sid: str = None
    number: str = None
        
    @classmethod
    async def twilio_send_message(cls, to_number: str, body: str, from_number: str = phone_number) -> object:
        message = cls.twilio_client.messages.create(to=to_number,from_=from_number,body=body)
        #TODO: possibly change this to query the URI for status once it has been sent or received
        if message._properties["status"] == "queued":
            cls.call_sid = message.sid
            cls.number = message.to
            return cls
        return None

    @classmethod
    async def twilio_call_with_recording(cls, to_number: str, body: str, from_number: str = phone_number) -> object:
        twiml = f'''<Response>
            <Say>
                {body}
            </Say>
        </Response>'''
        
        try:
            call = cls.twilio_client.calls.create(to=to_number, from_=from_number, twiml=twiml)
            cls.call_sid = call.sid
            cls.number = call.to
        except twilio.base.exceptions.TwilioException as e:
            logger.error(e)
            return None

        return cls

    @classmethod
    def get_call_info(cls, sid: str):
        if sid.find('SM') == -1:
            return cls.twilio_client.calls(sid).fetch()
        return cls.twilio_client.messages(sid).fetch()

    @classmethod
    def get_caller_info(cls, number: str):
        return cls.twilio_client.lookups.v1.phone_numbers(number).fetch()

@database_sync_to_async
def twilio_database_routine(number: str, call_sid: str, call_type:str, msg_type: str, message: str):
    tc = twilio_controller
    try:
        caller = Caller.objects.get(number=number)
    except Caller.DoesNotExist:
        caller = tc.get_caller_info(number=number)
        Caller(number=number, country=caller['country_code']).save()
        caller = Caller.objects.get(number=number)

    try:
        call = Call.objects.get(sid=call_sid)
    except Call.DoesNotExist:
        call = tc.get_call_info(sid=call_sid)

        duration = 0
        if hasattr(call, 'duration'):
            duration = call.duration
        Call(sid=call_sid, length_of_call=duration, caller_id=caller.id, call_type=call_type).save()
        call = Call.objects.get(sid=call_sid)
    
    Message(call_id=call.id,number=number,message_type=msg_type,message=message).save()