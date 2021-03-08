import React, {Component} from "react";
import {connect} from "react-redux";

import {Link} from "react-router-dom";


class Login extends Component {

  state = {
    username: "",
    password: "",
  }

  onSubmit = e => {
    e.preventDefault();
  }

  componentDidMount = e => {
    document.getElementById('csrfmiddlewaretoken').value = getCookie("csrftoken");
  }

  render() {
    return (
      <form onSubmit={this.onSubmit} action="/api/login/" method="post">
        <input type="hidden" id="csrfmiddlewaretoken" name="csrfmiddlewaretoken"/>
        <fieldset>
          <legend>Login</legend>
          <p>
            <label htmlFor="username">Username: </label>
            <input
              type="text" id="username"
              onChange={e => this.setState({username: e.target.value})} />
          </p>
          <p>
            <label htmlFor="password">Password: </label>
            <input
              type="password" id="password"
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

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
      }
  }
  return cookieValue;
}

const mapStateToProps = state => {
  return {};
}

const mapDispatchToProps = dispatch => {
  return {};
}

export default connect(mapStateToProps, mapDispatchToProps)(Login);