import React, {Component} from "react";
import Chat from "./Chat";
import "./styles/numbers.css";

class Numbers extends Component {
  constructor(props) {
    super(props);

    this.state = {
      numbersList: [],
      messages: [],
      connectedCell: '',
    };
  }

  componentDidMount() {
    this.getNumbers();
  }

  changeColor(id) {
    if (id == this.state.connectedCell) {
      return false;
    }

    if (this.state.connectedCell !== '') {
      document.getElementById(this.state.connectedCell).style.backgroundColor = (document.getElementById(this.state.connectedCell).style.backgroundColor == '') ? '#DDDDDD' : '';
    }
    
    document.getElementById(id).style.backgroundColor = (document.getElementById(id).style.backgroundColor == '') ? '#DDDDDD' : '';

    return true;
 }

 editNumbers() {
  if (this.state.connectedCell === '') {
  }
  return
 }

  async getMessages(number) {
    if (!this.changeColor(number)) {
      console.log("already connected. doing nothing");
      return
    }
    var url = "/api/messages/"+number+"/";
    this.state.messages = await this.get(url);
    this.setState({messages: this.state.messages.map((message) => message['message'])});

    Chat.loadChatRoom(number, this.state.messages);
    this.setState({connectedCell: number});
  }

  getNumbers() {
    var url = "/api/numbers/";
    this.get(url).then((result) => {
      var numbers = result;
      this.setState({numbersList: numbers.map((number) => 
        //in Javascript if I pass just the function then it is called upon creation but if I pass the reference, i.e. () => this.getMessages,
        //then it will be called only after action
        <tr key={number["number"]} onClick={() => this.getMessages(number["number"])}>
          <td id={number["number"]}>{number['number'] }</td>
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
        <input onClick={this.editNumbers()} id="edit-numbers-button" type="button" value="Edit"/>
      </div>
    )
  }
}

export default Numbers;