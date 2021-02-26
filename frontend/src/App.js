import React, { Component } from "react";
import {Route, Switch, BrowserRouter} from "react-router-dom";
import { Provider } from "react-redux";
import Login from "./components/Login";
import NotFound from "./components/NotFound";
import Register from "./components/Register";
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
            <Route component={NotFound} />
          </Switch>
        </BrowserRouter>
      </Provider>
    );
  }
}

// //   render() {
// //     return (
// //       <Provider store={store}>
// //         <BrowserRouter>
// //           <Switch>
// //             <Route exact path="/" component={Login}/>
// //           </Switch>
// //         </BrowserRouter>
// //       </Provider>
// //       <ul>
// //         {this.state.data.map(contact => {
// //           return (
// //             <li key={contact.id}>
// //               {contact.name} - {contact.email}
// //             </li>
// //           );
// //         })}
// //       </ul>
// //     );
// //   }
// // }

export default App;

const container = document.getElementById("app");
render(<App />, container);