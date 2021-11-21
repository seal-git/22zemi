import React from 'react'
import "./../../css/Selection.css"
// パッケージからインポート
import axios from "axios"
import { useEffect, useState } from "react"
// 他のファイルからインポート
import RestaurantInformation from './selection-components/RestaurantInformation'
import RestaurantInformationDeck from './selection-components/RestaurantInformationDeck'
import noImageIcon from "./../../img/no_image.png"
import tutorialImage from "./../../img/tutorial1all.png"

const initDataList = [{
  "Name": "Loading...",
  "Images": [noImageIcon ],
  "Price": "",
  "Restaurant_id": "init",
}]
const emptyDataList = [{
  "Name": "No Data:\n検索条件を変えてみてください",
  "Images": [noImageIcon ],
  "Restaurant_id": "empty",
}]
const tutorialDataList = [{
  "Name": "",
  "Images": [tutorialImage ],
  "Price": "",
  "Restaurant_id": "tutorial",
}]

// カードのスタイル
var wrapperStyle = {
  margin: 0,
  height: '100%',
  position: 'absolute',
}

/*
 スワイプでお店を選ぶコンポーネント
 */
function Selection(props) {
  const [dataLists, setDataLists] = useState(
        props.tutorialIsOn?{ 
            "topDataList": [],
            "standbyDataList": tutorialDataList,
        }:{
            "topDataList": initDataList,
            "standbyDataList": [],
        }
  )
  let isLoading = false
  let hiddenDataList = null

  // APIからお店のデータを得る
  const getInfo = (type="init", topDataList=null) => {
    if (isLoading) return;
    isLoading = true
    
    const params = {
      ...props.paramsForSearch,
      'open_hour': +props.paramsForSearch['open_hour_str'].slice(0, 2)
    }
    console.log(params);
    axios.post('/api/info', {
      params: params
    })
      .then(function (response) {
        console.log(response)
        let receivedDataList = response['data']
        let cardNum = receivedDataList.length
        if (cardNum > 0) {
          console.log(receivedDataList[0])
          const newDataList = receivedDataList
          if(type==="init"){
            console.log("received topDataList")
            isLoading = false
            getInfo("standby",newDataList)
          } 
          else if(type==="standby"){
            setDataLists({
              "topDataList":topDataList,
              "standbyDataList":newDataList,
            })
          } 
          else if(type==="preload"){
            hiddenDataList = newDataList
          } 
          else {
            console.log("undefined type")
          }
        } else {
          if(type==="init"){
            setDataLists({
              "topDataList":emptyDataList,
              "standbyDataList":emptyDataList,
            })
          }
          else if(type==="standby"){
            setDataLists({
              "topDataList":topDataList,
              "standbyDataList":emptyDataList,
            })
          } 
          else if(type==="preload"){
            hiddenDataList = emptyDataList
          } else {
            console.log("undefined type")
          }
        }
        isLoading = false
      })
      .catch((error) => {
        console.log("error:", error)
      });
  }
  const setPreloadedDataList = () =>{
    if(hiddenDataList!==null){
      const newStandbyDataList = hiddenDataList 
      hiddenDataList = null
      setDataLists({
        "topDataList":dataLists.standbyDataList,
        "standbyDataList":newStandbyDataList,
      })
    }
  }

  useEffect(() => {
      if(props.tutorialIsOn===false){
          getInfo("init",null)
      }else{
          getInfo("standby",tutorialDataList)
      }
    // Mount 時にだけ呼び出す
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // APIにキープ・リジェクトを送信する
  const sendFeeling = (feeling, restaurant_id) => {
    // tutorial card は送らない
    if(restaurant_id.indexOf('tutorial')!==-1) return;

    axios.post('/api/feeling', {
      params: {
        user_id: props.paramsForSearch['user_id'],
        group_id: props.paramsForSearch['group_id'],
        restaurant_id: restaurant_id,
        feeling: feeling,
      }
    })
      .then(function (response) {
        console.log(response)
        const v = response.data?response.data:0
        props.keepNumberRef.current = v
      })
      .catch((error) => {
        console.log("error:", error);
      });
  }

  // 各ボタンに対応する関数
  const reject = (restaurant_id) => {
    console.log("reject")
    if (isLoading) return null
    sendFeeling(false, restaurant_id)
  }
  const keep = (restaurant_id) => {
    console.log("keep:", restaurant_id)
    if (isLoading) return null
    sendFeeling(true, restaurant_id)
  }

  let renderStandbyRestaurantInformation = () =>{
    if(dataLists.standbyDataList===null) return null
    if(dataLists.standbyDataList.length===0) return null
    return (
      <RestaurantInformation 
        data={dataLists.standbyDataList[0]}
        wrapperStyle={wrapperStyle}
        keep={()=>{ console.log("pushed")}}
        reject={()=>{console.log("pushed")}}
        groupId={props.paramsForSearch['group_id']}
        inviteUrl={props.inviteUrl}
      />
    )
  }

  let renderRestaurantInformationDeck = () =>{
    if(dataLists.topDataList===null) return null
    return (
      <RestaurantInformationDeck
        topDataList={dataLists.topDataList}
        standbyDataList={dataLists.standbyDataList}
        hasRestaurant={
          dataLists.topDataList !== initDataList 
          && dataLists.topDataList !== emptyDataList}
        wrapperStyle={wrapperStyle}
        keep={keep}
        reject={reject}
        getInfo={getInfo}
        setPreloadedDataList={setPreloadedDataList}
        groupId={props.paramsForSearch['group_id']}
        inviteUrl={props.inviteUrl}
      />
    )
  }

  return (
    <div className="Selection-wrapper">
      <div className="Selection-header">
      </div>
      <div className="Selection" id={"selection"}>
        { renderStandbyRestaurantInformation() }
          {/* <RestaurantInformation data={dataList[idx]} wrapperStyle={wrapperStyle} /> */}
        { renderRestaurantInformationDeck() }
        {/* { renderButtonToInvite() } */}
        {/* { renderButtonToShowComment() } */}
      </div>
    </div>
  )
}

export default Selection