import React, {Component} from "react";
import "./styles/livechat.css"

class LiveChat extends Component {
    state = {
        ws: WebSocket,
        connectedNumber: '',
    }

    loadChatRoom(number, messages) {
        this.initWebSocket(number);

        document.getElementById("chat-log").value = '';
        messages.map((message) => {
            document.getElementById("chat-log").value += (message + '\n');
        })
    }

    initWebSocket(number) {
        //check to keep number of open websocket connections to 1
        if (this.state.ws.readyState === this.state.ws.OPEN) {
            console.log("closing connection to socket: /ws/chat/"+number)
            this.ws.close();
        }
        console.log("connecting to socket: /ws/chat/"+number)
        this.setState({ws: new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + number + '/'
        )});
        this.setState({connectedNumber: number});
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