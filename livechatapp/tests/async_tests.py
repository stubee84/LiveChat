from channels.testing import WebsocketCommunicator
from ..consumers import GeneralChatConsumer
import json, pytest

@pytest.mark.asyncio
async def test_general_consumer():
    communicator = WebsocketCommunicator(GeneralChatConsumer, path="/chat/general")
    print("test message")
    connected, subprotocol = await communicator.connect()
    assert connected

    send_msg = {"message":"test message"}
    await communicator.send_to(text_data=json.dumps(send_msg))
    rcv_msg = await communicator.receive_output()

    print(rcv_msg)
    assert send_msg == json.loads(rcv_msg['text'])

    await communicator.disconnect()