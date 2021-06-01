
class WS {
    static socket = null;
    static setWebSocket(endpoint) {
        if (this.socket !== null) {
            if (this.socket.readyState === this.socket.OPEN) {
                console.log("closing connection to socket: "+ this.socket.url)
                this.socket.close();
            }
        }
        this.socket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + endpoint + '/'
        );
        console.log("successfully connected to " + this.socket.url);
    }

    static receive(callback) {
        this.socket.onmessage = callback;
    }

    static send(msg) {
        this.socket.send(JSON.stringify(msg));
    }
}

export default WS;