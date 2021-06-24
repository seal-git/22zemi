import { useEffect, useState } from "react";
import Buttons from "./Buttons";
import RestaurantInformation from "./RestaurantInformation";
import axios from "axios";

// ひとりで決める
function Alone() {
  // APIからデータを得る
  const [idx, setIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [dataList, setDataList] = useState([{"Name":"Hello"}])
  const [data, setData] = useState(dataList[0])

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

  useEffect( ()=> {
    if(isLoading) {
      setIsLoading(false)
      getInfo()
    }
  },[])

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

  // 各ボタンに対応する関数
  const reject = () => {
    console.log("reject")
    if(isLoading) return;
    turnCard()
  }
  const keep = () => {
    console.log("keep")
    if(isLoading) return;
    turnCard()
  }
  const direct = () => {
    console.log("direct")
    window.open(data.UrlYahooMap)
  }
  const reserve = () => {
    console.log("reserve")
    window.open(data.UrlYahooLoco)
  }
  return (
    <div className="Alone">
        <RestaurantInformation data={data}/>
        <Buttons reject={reject} keep={keep} direct={direct} reserve={reserve}/>
    </div>
  );
}

export default Alone;
