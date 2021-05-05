import React, {Component} from "react";
import {connect} from "react-redux";
import cookies from "./Cookies"
import {Link} from "react-router-dom";


class Login extends Component {

  state = {
    email: "",
    password: ""
  }

  onSubmit = e => {
    e.preventDefault();

    fetch("/api/login/", {
      method: "POST",
      headers:  {
        'X-CSRFTOKEN': cookies('csrftoken'),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({email: this.state.email, password: this.state.password})
    }).then(async response => {
      var data = await response.json();

      if (!response.ok) {
        var err = (data && data.message) || response.status;
        console.error(err);
        return Promise.reject(err);
      }

      this.setState({email: "", password: ""});
      window.location.assign("/chat/")
    }).catch(error => {
      console.error(error);
      this.setState({email: "", password: ""});
      return Promise.reject(error);
    });
  }

  render() {
    return (
      <form onSubmit={this.onSubmit} action="/api/login/" method="post">
        <fieldset>
          <legend>Login</legend>
          <p>
            <label htmlFor="username">Username: </label>
            <input
              type="text" id="email" name="email"
              onChange={e => this.setState({email: e.target.value})} />
          </p>
          <p>
            <label htmlFor="password">Password: </label>
            <input
              type="password" id="password" name="password"
              onChange={e => this.setState({password: e.target.value})} />
          </p>
          <p>
            <input type="submit" value="Login"/>
          </p>
          <p>
            Don't have an account? <Link to="/register">Register</Link>
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

export default connect(mapStateToProps, mapDispatchToProps)(Login);