import React, {Component} from "react";
import "./styles/livechat.css"

class LiveChat extends Component {
    constructor(props) {
        super(props);

        this.ws = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + 'general/'
        );

        this.receive()
    }

    componentDidMount() {
        document.querySelector('#chat-message-input').focus();
    }

    receive() {
        this.ws.onmessage = message => {
            var data = JSON.parse(message.data);
            document.querySelector('#chat-log').value += (data.message + '\n');
        }
    }

    loadChatRoom(number, messages) {
        this.initWebSocket(number);

        document.querySelector("#chat-log").value = '';
        messages.map((message) => {
            document.querySelector("#chat-log").value += (message + '\n');
        })
    }

    initWebSocket(number) {
        //check to keep number of open websocket connections to 1
        if (this.ws.readyState === this.ws.OPEN) {
            console.log("closing connection to socket: "+ this.ws.url)
            this.ws.close();
        }

        this.ws = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + number + '/'
        );
        console.log("successfully connected to " + this.ws.url);
        
        this.receive();
    }

    send(key) {
        if (key === 'Enter' || key === 0) {
            var text = document.querySelector("#chat-message-input").value;
            var type = document.querySelector("#chat-message-destination").value;
            
            var msg = {
                "message": text,
                "type": type,
                "stream": "False"
            };
            this.ws.send(JSON.stringify(msg));

            document.querySelector("#chat-message-input").value = "";
        }
    }
    
    render () {
        return (
            <div id="dashboard-chat-container">
                <h2 id="chat-window">Chat</h2>
                <div id="chat-text-container">
                    <textarea id="chat-log" cols="100" rows="20"></textarea>
                </div>
                <div id="chat-input-container">
                    <div id="input-destination">
                        <select id="chat-message-destination">
                            <option value="chat">Chat</option>
                            <option value="sms">SMS</option>
                            <option value="inbound_record_call">Inbound Recorded Call</option>
                            <option value="outbound_text_call">Outbound Text Call</option>
                            <option value="live_inbound_transcription">Live Inbound Transcription</option>
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

export default LiveChat;