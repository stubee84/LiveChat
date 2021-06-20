import React, {Component} from "react";
import Chat from "./Chat";
import Numbers from "./Numbers";
import Logout from "./Logout";
import "./styles/dashboard.css"

class Dashboard extends Component {
    
    render() {
        return (
            <div className="dashboard-container">
                <div className="numbers-container">
                    <Numbers></Numbers>
                </div>
                <div className="chat-container">
                    <Chat></Chat>
                </div>
                <div className="logout-container">
                    <Logout></Logout>
                </div>
            </div>
        )
    }
}

export default Dashboard;