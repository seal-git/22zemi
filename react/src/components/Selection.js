import { useEffect, useState } from "react";
import Buttons from "./Buttons";
import RestaurantInformation from "./RestaurantInformation";
import ButtonToChangeMode from "./ButtonToChangeMode";
import axios from "axios";

// スワイプでお店を選ぶ画面
function Selection() {
  const [idx, setIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [dataList, setDataList] = useState([{"Name":"Hello","Images":[""]}])
  const [data, setData] = useState(dataList[0])

  // APIからお店のデータを得る
  const getInfo = () => {
    axios.post('/api/info',{ params: {
      user_id:1,
      group_id:1
    }
    })
    .then(function(response){
      console.log(response)
      let dataList = response['data']
      console.log(dataList[0])
      setIndex(0)
      setData(dataList[0])
      setDataList(dataList)
      setIsLoading(false)
    })
    .catch((error) => {
      console.log("error:",error);
    });
  }

  // 初レンダリング時のみ自動でデータを得る
  useEffect( ()=> {
    if(isLoading) {
      setIsLoading(false)
      getInfo()
    }
  },[])

  // カードをめくる
  const turnCard = () => {
    if(idx>=dataList.length) return
    const nextIdx = idx + 1
    if(nextIdx===dataList.length){
      setIsLoading(true)
      getInfo()
    }else{
      setIndex(nextIdx)
      setData(dataList[nextIdx])
    }
  }

  // APIにキープ・リジェクトを送信する
  const sendFeeling = (feeling) => {
    axios.post('/api/feeling',{ params: {
      user_id:1,
      restaurant_id: data.Restaurant_id,
      feeling: feeling, 
    }
    })
    .then(function(response){
      console.log(response)
      turnCard()
    })
    .catch((error) => {
      console.log("error:",error);
    });
  }

  // 各ボタンに対応する関数
  const reject = () => {
    console.log("reject")
    if(isLoading) return;
    turnCard()
    sendFeeling(false)
  }
  const keep = () => {
    console.log("keep")
    if(isLoading) return;
    turnCard()
    sendFeeling(true)
  }
  return (
    <div className="Selection">
        <ButtonToChangeMode mode={"Group"}/>
        <RestaurantInformation data={data}/>
        <Buttons reject={reject} keep={keep}/>
    </div>
  );
}

export default Selection;
