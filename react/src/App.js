import logo from './logo.svg';
import './App.css';

import axios from 'axios';

function get_api(){
  let result = "r";
  axios.post('/api/get_sample_db',{
  })
  .then(function(response){
    console.log(response)
    result = JSON.stringify(response['data']['content']);
    console.log("result:",result)
  })
  .catch((error) => {
    console.log("error:",error);
    result = "error"
  });
  return result;
};
let result = get_api();

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React!
        </a>
        <p>
          {result}
        </p>
      </header>
    </div>
  );
}

export default App;
