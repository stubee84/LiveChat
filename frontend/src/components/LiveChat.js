import React, {Component} from "react";

class LiveChat extends Component {

    componentDidMount() {
        this.initWebSocket();
    }

    initWebSocket() {

    }
    render () {
        return (
            <div id="dashboard-chat-container">
                <h1 id="chat-window">Chat</h1>
                <div id="chat-text-container">
                    <textarea id="chat-log" cols="100" rows="20"></textarea>
                </div>
                <div id="chat-input-container">
                    <div id="input-text">
                        <input id="chat-message-input" type="text" size="100"/>
                    </div>
                    <div id="input-button">
                        <input id="chat-message-submit" type="button" value="Send"/>
                    </div>
                </div>
            </div>
        );
    }
}

export default LiveChat;