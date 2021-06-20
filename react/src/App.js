import './App.css';
import Alone from './components/Alone'
import ApiTest from './components/ApiTest'
import Entrance from './components/Entrance'
import Group from './components/Group';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

function App() {
  return (
    <div className="App">
      <Router>
        <Switch>
          <Route path="/" exact><Entrance /></Route>
          <Route path="/alone" exact><Alone /></Route>
          <Route path="/group" exact><Group /></Route>
          <Route path="/api-test" exact><ApiTest /></Route>
        </Switch>
      </Router>
    </div>
  );
}

export default App;
