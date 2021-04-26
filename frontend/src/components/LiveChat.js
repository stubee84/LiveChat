import React, {Component} from "react";
import "./styles/livechat.css"

class LiveChat extends Component {
    loadChatRoom(number, messages) {
        this.initWebSocket(number);

        document.querySelector("chat-log").value = '';
        messages.map((message) => {
            document.querySelector("chat-log").value += (message + '\n');
        })
    }

    initWebSocket(number) {
        this.chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + number + '/'
        );
    }

    send(number) {
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
                            <option value="live_inbound_transcription">Live Inbound Transcription</option>
                            <option value="live_outbound_text_to_speech">Live outbound text to speech</option>
                        </select>
                    </div>
                    <div id="input-text">
                        <input onKeyUp={this.send()} id="chat-message-input" type="text" size="100"/>
                    </div>
                    <div id="input-button">
                        <input onClick={this.send()} id="chat-message-submit" type="button" value="Send"/>
                    </div>
                </div>
            </div>
        );
    }
}

export default LiveChat;