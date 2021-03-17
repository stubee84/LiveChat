import React, {Component} from "react";
import {connect} from "react-redux";

import {Link} from "react-router-dom";


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
        console.error(err);
        return Promise.reject(err);
      }

      this.setState({email: "", password1: "", password2: ""})
      window.location.assign = "/login/"
    }).catch(error => {
      console.error(error);
      this.setState({email: "", password1: "", password2: ""})
      return Promise.reject(error)
    });
  }

  render() {
    return (
      <form onSubmit={this.onSubmit} action="/api/register/" method="post">
        <fieldset>
          <legend>Register</legend>
          <p>
            <label htmlFor="email">Email: </label>
            <input
              type="text" id="email"
              onChange={e => this.setState({email: e.target.value})} />
          </p>
          <p>
            <label htmlFor="password1">Password: </label>
            <input
              type="password" id="password1"
              onChange={e => this.setState({password1: e.target.value})} />
          </p>
          <p>
            <label htmlFor="password2">Repeat: </label>
            <input
              type="password" id="password2"
              onChange={e => this.setState({password2: e.target.value})} />
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

const mapStateToProps = state => {
  return {};
}

const mapDispatchToProps = dispatch => {
  return {};
}

export default connect(mapStateToProps, mapDispatchToProps)(Register);