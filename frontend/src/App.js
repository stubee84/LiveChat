import React, { Component } from "react";
import {Route, Switch, BrowserRouter} from "react-router-dom";
import { Provider } from "react-redux";
import "core-js/stable";
import "regenerator-runtime/runtime";

import Login from "./components/Login";
import NotFound from "./components/NotFound";
import Register from "./components/Register";
import Dashboard from "./components/Dashboard";
import { render } from "react-dom";

import { createStore } from "redux";
import liveChatApp from "./reducers";

let store = createStore(liveChatApp);

class App extends Component {
  render() {
    return (
      <Provider store={store}>
        <BrowserRouter>
          <Switch>
            <Route exact path="/" component={Login} />
            <Route exact path="/login" component={Login} />
            <Route exact path="/register" component={Register} />
            <Route exact path="/chat" component={Dashboard} />
            <Route component={NotFound} />
          </Switch>
        </BrowserRouter>
      </Provider>
    );
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);