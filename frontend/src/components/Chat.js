import React, {Component} from "react";
import WS from "./WebSocket";
import "./styles/livechat.css"

class Chat extends Component {
    constructor(props) {
        super(props);

        WS.setWebSocket("general");
        Chat.receive();
    }
    componentDidMount() {
        document.querySelector('#chat-message-input').focus();
    }

    static loadChatRoom(number, messages) {
        WS.setWebSocket(number);

        document.querySelector("#chat-text-log").value = '';
        messages.map((message) => {
            document.querySelector("#chat-text-log").value += (message + '\n');
        });
        this.receive();
    }

    static receive() {
        WS.receive(message => {
            var data = JSON.parse(message.data);

            if ('stream' in data) {
                document.querySelector('#chat-stream-log').value += (data.message + '\n');
            } else {
                document.querySelector('#chat-text-log').value += (data + '\n');
            }
        });
    }

    send(key) {
        if (key === 'Enter' || key === 0) {
            var text = document.querySelector("#chat-message-input").value;
            var type = document.querySelector("#chat-message-destination").value;

            var msg = {
                "message": text,
            };
            switch(type) {
                case "outbound_call":
                    msg['call'] = true;
                    break;
                case "live_outbound_text_to_speech":
                    msg['stream'] = true;
                    break;
                case "sms":
                    msg['sms'] = true;
                    break;
            }
            
            WS.send(msg);

            document.querySelector("#chat-message-input").value = "";
        }
    }
   
    render () {
        return (
            <div id="dashboard-chat-container">
                <h2 id="chat-window">Chat</h2>
                <div id="chat-stream-container">
                    <h3 id="chat-stream-window">Stream</h3>
                    <textarea id="chat-stream-log" cols="100" rows="2"></textarea>
                </div>
                <div id="chat-text-container">
                    <h3 id="chat-text-window">Text</h3>
                    <textarea id="chat-text-log" cols="100" rows="20"></textarea>
                </div>
                <div id="chat-input-container">
                    <div id="input-destination">
                        <select id="chat-message-destination">
                            <option value="chat">Chat</option>
                            <option value="sms">SMS</option>
                            <option value="outbound_call">Outbound Call</option>
                            <option value="live_outbound_text_to_speech">Live outbound text to speech</option>
                        </select>
                    </div>
                    <div id="input-text">
                        <input onKeyUp={e => this.send(e.key)} id="chat-message-input" type="text" size="100"/>
                    </div>
                    <div id="input-button">
                        <input onClick={e => this.send(e.button)} id="chat-message-submit" type="button" value="Send"/>
                    </div>
                </div>
            </div>
        );
    }
}

export default Chat;