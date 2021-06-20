
import { useState } from "react"
import axios from 'axios';

function Home() {
  // setResult で result の値を更新するとリレンダリングが走る
  const [ result, setResult ] = useState('--')

  // 飲食店の情報を api に要求して結果を result に反映させる
  const getInfo = () => {
    axios.post('/api/info',{ params: {
      user_id:1,
      group_id:1
    }
    })
    .then(function(response){
      let data = response['data'][0]
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

  return (
    <div className="Home">
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

export default Home;
