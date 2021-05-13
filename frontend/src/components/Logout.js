import React, {Component} from "react";
import {Link} from "react-router-dom";


class Logout extends Component {

  get(url) {
    var promise = fetch(url, {
      method: "GET",
      headers:  {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
    }).then(async () => {
      console.log("successfully logged out")
    }).catch(error => {
      console.error(error);
      return Promise.reject(error);
    });
    return promise;
  }

  render() {
    return (
      <p>
        <Link onClick={() => this.get('/logout')} to="/">Logout</Link>
      </p>
    )
  }
}

export default Logout;