import React, {Component} from "react";
import LiveChat from "./LiveChat";
import Numbers from "./Numbers";

class Dashboard extends Component {
    
    render() {
        return (
            <div id="dashboard-container">
                {Numbers}
                {LiveChat}
            </div>
        )
    }
}

export default Dashboard;