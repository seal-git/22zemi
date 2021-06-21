import './App.css';
import ApiTest from './components/ApiTest'
import Home from './components/Home'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

function App() {
  return (
    <div className="App">
      <div className="App-header"></div>
      <Router>
        <Switch>
          <Route path="/" exact><Home /></Route>
          <Route path="/api-test" exact><ApiTest /></Route>
        </Switch>
      </Router>
    </div>
  );
}

export default App;
