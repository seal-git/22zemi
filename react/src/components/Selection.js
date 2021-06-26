import { useEffect, useState } from "react";
import Buttons from "./Buttons";
import RestaurantInformation from "./RestaurantInformation";
import ButtonToChangeMode from "./ButtonToChangeMode";
import axios from "axios";

// スワイプでお店を選ぶ画面
function Selection(props) {
  const [idx, setIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [dataList, setDataList] = useState([{"Name":"Waiting...","Images":[""]}])

  // APIからお店のデータを得る
  const getInfo = () => {
    const params = {"user_id":props.userId}
    if(props.mode==="Group"){
        params["group_id"] = props.groupId
    }
    axios.post('/api/info',{ 
        params: params
    })
    .then(function(response){
      console.log(response)
      let dataList = response['data']
      console.log(dataList[0])
      setIndex(0)
      setDataList(dataList)
      setIsLoading(false)
    })
    .catch((error) => {
      console.log("error:",error);
    });
  }

  // 初レンダリング時に自動でデータを得る
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
    }
  }

  // APIにキープ・リジェクトを送信する
  const sendFeeling = (feeling) => {
    axios.post('/api/feeling',{ params: {
      user_id:1,
      restaurant_id: dataList[idx].Restaurant_id,
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
    sendFeeling(false)
  }
  const keep = () => {
    console.log("keep")
    if(isLoading) return;
    sendFeeling(true)
  }
  const turnMode = (groupId) => {
      console.log("Selection:turnMode")
      props.turnMode(groupId)
      setIsLoading(true)
      setDataList([{"Name":"Waiting...","Images":[]}])
      getInfo()
  }
  return (
    <div className="Selection">
        <ButtonToChangeMode mode={props.mode} turnMode={turnMode}/>
        <RestaurantInformation data={dataList[idx]}/>
        <Buttons reject={reject} keep={keep}/>
    </div>
  );
}

export default Selection;
