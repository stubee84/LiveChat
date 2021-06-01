import React, {Component} from "react";
import Chat from "./Chat";
import Numbers from "./Numbers";
import Logout from "./Logout";
// import { render } from "react-dom";
import "./styles/dashboard.css"

class Dashboard extends Component {
    
    render() {
        return (
            <div id="dashboard-container">
                <div id="numbers-container">
                    <Numbers></Numbers>
                </div>
                <div id="chat-container">
                    <Chat></Chat>
                </div>
                <div id="logout-container">
                    <Logout></Logout>
                </div>
            </div>
        )
    }
}

export default Dashboard;