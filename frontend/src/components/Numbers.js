import React, {Component} from "react";
import Chat from "./Chat";
import "./styles/numbers.css";
import cookies from "./Cookies"

class Numbers extends Component {
  constructor(props) {
    super(props);

    this.state = {
      numbersList: [],
      messages: [],
      connectedCell: '',
    };
    this.numReg = new RegExp('^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$')
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

  numberExists(number) {
    if (document.getElementById(number)) {
      return true;
    }
    return false;
  }

  addRow(value) {
    var table = document.getElementById("numbers-table");
    var row = table.insertRow(-1);
    var cell = row.insertCell(0);
    cell.innerHTML = value;
  }

  async addNumber(event) {
    if (event.key === 'Enter' || event.keyCode === 13) {
      var number = document.getElementById("add-number").value;

      if (!this.numReg.test(number)) {
        alert("invalid number format");
        return;
      }
      if (this.numberExists(number)) {
        alert("Number already added");
        return;
      }

      await this.send("/api/numbers/"+number+"/", "POST");
      await this.getNumbers(number);
    }
  }

  removeRow(value) {
    var table = document.getElementById("numbers-table");
    var rows = table[0].rows;

    var deleted = false;
    rows.foreach((row, i) => {
      var cell = row.cells[0];
      if (cell.innerHTML === value) {
        table.deleteRow(i);
        deleted = true;
        return;
      }
    });
    if (!deleted) {
      alert(value + " does not exist in table");
    }
  }

  async removeNumber() {
    var number = this.state.connectedCell;
    if (number === '') {
      alert("select a cell first to remove");
      return;
    }

    await this.send("/api/numbers/"+number+"/", "DELETE");
    await this.getNumbers(number);
    this.state.connectedCell = '';
  }

  async getMessages(number) {
    if (!this.changeColor(number)) {
      console.log("already connected. doing nothing");
      return
    }
    var url = "/api/messages/"+number+"/";
    this.state.messages = await this.send(url, "GET");
    this.setState({messages: this.state.messages.map((message) => message['message'])});

    Chat.loadChatRoom(number, this.state.messages);
    this.setState({connectedCell: number});
  }

  async getNumbers() {
    var url = "/api/numbers/";
    this.send(url, "GET").then((result) => {
      var numbers = result;
      this.setState({numbersList: numbers.map((number) => 
        //in Javascript if I pass just the function then it is called upon creation but if I pass the reference, i.e. () => this.getMessages,
        //then it will be called only after action
        <tr key={number["number"]} onClick={() => this.getMessages(number["number"])}>
          <td id={number["number"]}>{number['number']}</td>
        </tr>
      )});
    });
  }

  send(url, method) {
    var promise = fetch(url, {
      method: method,
      headers:  {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': cookies('csrftoken'),
      },
    }).then(async response => {
      var data = await response.json();
        
      if (!response.ok) {
        var err = (data && data.message) || response.status;
        alert(data);
        return Promise.reject(err);
      }
      
      return data;
    }).catch(error => {
      console.error(error);
      // return Promise.reject(error);
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
        <div id="input-destination">
          <p>
            <input onKeyUp={e => this.addNumber(e)} type="text" placeholder="Add Number" size="10" id="add-number"/>
          </p>
          <p>
            <input onClick={e => this.removeNumber()} type="button" value="Remove Number" id="remove-number"/>
          </p>
          {/* <select id="modify-numbers-table" onChange={() => this.modify()}>
            <option></option>
            <option value="add">Add</option>
            <option value="remove">Remove</option>
          </select> */}
        </div>
      </div>
    )
  }
}

export default Numbers;