import { useState, useEffect } from "react"
import axios from 'axios';

// APIを試す画面
function ApiTest() {
  // setResult で result の値を更新するとリレンダリングが走る
  const [ result, setResult ] = useState('--')

  // 飲食店の情報を api に要求して結果を result に反映させる
  const getInfo = () => {
    axios.post('/api/info',{ params: {
      user_id:"hoge",
      group_id:"fuga"
    }
    })
    .then(function(response){
      let data = response['data'][0]
      console.log(data)
      let restaurantName = data['Name']
      let images = data['Images']
      console.log("restaurantName:",restaurantName)
      console.log("images:",images)
      setResult(restaurantName)
    })
    .catch((error) => {
      console.log("error:",error);
    });
  }

  useEffect( ()=> {
    getInfo()
  },[])

  return (
    <div className="ApiTest">
      <p>
        Hello!
      </p>
        {<p>{result}</p>}
        <button onClick={ ()=>{ getInfo() } }>
          Update
        </button>
    </div>
  );
}

export default ApiTest;
