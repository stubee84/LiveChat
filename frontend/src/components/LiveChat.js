import React, {Component} from "react";
import "./styles/livechat.css"

class LiveChat extends Component {
    loadChatRoom(number) {
        this.initWebSocket(number);
        document.querySelector("chat-log").value = '';
        document.querySelector("chat-log").value += (message + '\n');
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