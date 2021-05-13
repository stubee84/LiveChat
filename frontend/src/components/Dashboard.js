import React, {Component} from "react";
import LiveChat from "./LiveChat";
import Numbers from "./Numbers";
import Logout from "./Logout";
import "./styles/dashboard.css"

class Dashboard extends Component {
    
    render() {
        return (
            <div id="dashboard-container">
                <div id="numbers-container">
                    <Numbers></Numbers>
                </div>
                <div id="chat-container">
                    <LiveChat></LiveChat>
                </div>
                <div id="logout-container">
                    <Logout></Logout>
                </div>
            </div>
        )
    }
}

export default Dashboard;