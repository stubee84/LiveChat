import React, {Component} from "react";
import {Link} from "react-router-dom";
import "./styles/register.css"


class Register extends Component {

  constructor(props) {
    super(props);

    this.state = {
      email: "",
      password1: "",
      password2: "",
    };
  }

  checkPassword() {
    if (this.state.password1 !== this.state.password2) {
      return false;
    }

    return true;
  }

  onSubmit = e => {
    e.preventDefault();
    
    //setState is an asynchronouse function but is not awaitable
    this.setState({
      email: document.querySelector("#email").value,
      password1: document.querySelector("#password1").value,
      password2: document.querySelector("#password2").value
    }, () => {
      if (!this.checkPassword()) {
        alert("password fields do not match");
        this.setState({email: "", password1: "", password2: ""});
        return
      }

      fetch("/api/register/", {
        method: "POST",
        headers:  {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({email: this.state.email, password: this.state.password1})
      }).then(async response => {
        var data = await response.json();
        
        if (!response.ok) {
          var err = (data && data.message) || response.status;
          alert(data);
          return Promise.reject(err);
        }
  
        this.setState({email: "", password1: "", password2: ""})
        this.props.history.push("/login/")
        // window.location.assign = "/login/"
      }).catch(error => {
        console.error(error);
        this.setState({email: "", password1: "", password2: ""})
        return Promise.reject(error)
      });
    });
  }

  render() {
    return (
      <form onSubmit={this.onSubmit} action="/api/register/" method="post">
        <fieldset className="register-container">
          <legend>Register</legend>
          <p><label htmlFor="email">Email</label></p>
          <p>
            <input
              type="text" id="email"
              // onChange={e => this.setState({email: e.target.value})}
            />
          </p>
          <p><label htmlFor="password1">Password</label></p>
          <p>
            <input
              type="password" id="password1"
              // onChange={e => this.setState({password1: e.target.value})}
            />
          {/* <p><label htmlFor="password2">Repeat</label></p> */}
          </p>
          <p>
            <input
              type="password" id="password2"
              // onChange={e => this.setState({password2: e.target.value})} 
            />
          </p>
          <p>
            <input type="submit" value="Register"/>
          </p>
          <p>
            Already Registered? <Link to="/login">Login</Link>
          </p>
        </fieldset>
      </form>
    )
  }
}

export default Register;