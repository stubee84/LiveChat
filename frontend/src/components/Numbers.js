import React, {Component} from "react";

class Numbers extends Component {

  state = {
    numbersList: [],
  };

  componentDidMount() {
    this.getNumbers();
  }

  getNumbers() {
    fetch("/api/numbers/", {
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
  
        this.setState({numbersList: data.map((number) => 
          <li id={number['number']}>{number['number']}</li>
        )});
      }).catch(error => {
        console.error(error);
        return Promise.reject(error)
      });
  }

  loadChatRoom() {

  }
//style="display:inline-block; border:1px solid #000; padding:20px;"
// style="list-style-type:none;"
  render() {
    return (
      <div className='dashboard-numbers-container'>
        <h1 id='numbers'>Numbers</h1>
        <ul onClick={this.loadChatRoom}>
          {this.state.numbersList}
          <li></li>
          <li><input type="button" value="Edit"/></li>
        </ul>
      </div>
    )
  }
}

export default Numbers;