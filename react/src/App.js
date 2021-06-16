import logo from './logo.svg';
import './App.css';

import axios from 'axios';


function App() {
  let result;
  axios.post('python-flask:5000/get_sample_db',{
  })
  .then(function(response){
    result = response['content'];
  })
  .catch((error) => {
    console.log(error);
  });

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <p>
          {result}
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React!!!
        </a>
      </header>
    </div>
  );
}

export default App;
