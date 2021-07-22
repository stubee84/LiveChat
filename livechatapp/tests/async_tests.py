from channels.testing import WebsocketCommunicator
from livechatapp.consumers import GeneralChatConsumer
from livechatapp.models import Message
from livechatapp.controllers.utils import database_routines as dr
import json, pytest

@pytest.mark.asyncio
@pytest.mark.django_db
async def test_general_consumer():
    communicator = WebsocketCommunicator(GeneralChatConsumer, path="/chat/general")
    connected, _ = await communicator.connect()
    assert connected

    send_msg = {"message":"test message"}
    await communicator.send_to(text_data=json.dumps(send_msg))
    rcv_msg = await communicator.receive_output()

    assert send_msg == json.loads(rcv_msg['text'])

    await communicator.disconnect()

    msg_saved = await dr.fetch(model=Message, message=send_msg['message'], message_type='C')
    assert send_msg['message'] == msg_saved.message