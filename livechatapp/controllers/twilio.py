from ..models import Caller, Call, Message
from .main import twilio_controller as tc
from channels.db import database_sync_to_async

@database_sync_to_async
def twilio_database_routine(number: str, call_sid: str, msg_type: str, message: str):
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
        Call(sid=call_sid, length_of_call=duration, caller_id=caller.id).save()
        call = Call.objects.get(sid=call_sid)
    
    Message(call_id=call.id,number=number,message_type=msg_type,message=message).save()