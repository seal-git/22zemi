import { useState } from "react"
import './App.css';

import axios from 'axios';

function App() {
  // setResult で result の値を更新するとリレンダリングが走る
  const [ result, setResult ] = useState('--')

  // post の結果を result に反映させる
  const getApi = () => {
    let result = "r";
    axios.post('/api/get_sample_db',{
    })
    .then(function(response){
      result = JSON.stringify(response['data']['content']);
      console.log("result:",result)
      setResult(result)
    })
    .catch((error) => {
      console.log("error:",error);
    });
  }

  return (
    <div className="App">
      <p>
        Hello!
      </p>
        {<p>{result}</p>}
        <button onClick={ ()=>{ getApi() } }>
          Update
        </button>
    </div>
  );
}

export default App;
