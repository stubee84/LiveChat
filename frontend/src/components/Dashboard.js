import React, {Component} from "react";
import LiveChat from "./LiveChat";
import Numbers from "./Numbers";
import "./styles/dashboard.css"

class Dashboard extends Component {
    
    render() {
        return (
            <div id="dashboard-container">
                <Numbers></Numbers>
                <LiveChat></LiveChat>
            </div>
        )
    }
}

export default Dashboard;