import React, {Component} from "react";
import LiveChat from "./LiveChat";
import "./styles/numbers.css";

class Numbers extends Component {

  lc = new LiveChat();
  state = {
    numbersList: [],
    messages: [],
  };

  componentDidMount() {
    this.getNumbers();
  }

  async getMessages(number) {
    var url = "/api/messages/"+number+"/";
    this.state.messages = await this.get(url);
    this.setState({messages: this.state.messages.map((message) => message['message'])});

    this.lc.loadChatRoom(number, this.state.messages);
  }

  getNumbers() {
    var url = "/api/numbers/";
    this.get(url).then((result) => {
      var numbers = result;
      this.setState({numbersList: numbers.map((number) => 
        //in Javascript if I pass just the function then it is called upon creation but if I pass the reference, i.e. () => this.getMessages,
        //then it will be called only after action
        <tr key={number["number"]} onClick={() => this.getMessages(number["number"])}>
          <td>{number['number'] }</td>
        </tr>
      )});
    });
  }

  get(url) {
    var promise = fetch(url, {
      method: "GET",
      headers:  {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
    }).then(async response => {
      var data = await response.json();
        
      if (!response.ok) {
        var err = (data && data.message) || response.status;
        console.error(err);
        return Promise.reject(err);
      }

      return data;
    }).catch(error => {
      console.error(error);
      return Promise.reject(error);
    });
    return promise;
  }

  render() {
    return (
      <div className='dashboard-numbers-container'>
        <h2 id='numbers-header'>Numbers</h2>
        <table className="numbers-table" id="numbers-table">
          <tbody id="numbers-table-body">
            {this.state.numbersList}
          </tbody>
        </table>
        <br></br>
        <input id="edit-numbers-button" type="button" value="Edit"/>
      </div>
    )
  }
}

export default Numbers;