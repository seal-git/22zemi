import React from 'react'
import "./Selection.css"
// パッケージからインポート
import axios from "axios"
import { useEffect, useState } from "react"
// 他のファイルからインポート
import ButtonToInvite from "./ButtonToInvite"
import RestaurantInformation from './RestaurantInformation'
import RestaurantInformationDeck from './RestaurantInformationDeck'
import noImageIcon from "..//img/no_image.png"
import sampleDataList from "./sampleData.json"

const initDataList = [{
  "Name": "Loading...",
  "Images": [noImageIcon, noImageIcon],
  "Price": "",
  "Restaurant_id": "init",
}]
const emptyDataList = [{
  "Name": "No Data:\n検索条件を変えてみてください",
  "Images": [noImageIcon, noImageIcon],
  "Restaurant_id": "empty",
}]

// カードのスタイル
var wrapperStyle = {
  margin: 0,
  height: '90vh',
  position: 'absolute',

}

// // カードの高さを指定する
// function getAdaptiveStyle() {
//     // let height = window.innerHeight
//     let height = document.getElementById("selection").getBoundingClientRect().height
//     let wrapperStyle = {
//         height: height,
//     }
//     return wrapperStyle
// };

// //windowサイズの変更検知のイベントハンドラを設定
// window.addEventListener('load', () => {
//     wrapperStyle = getAdaptiveStyle()
// })

/*
 スワイプでお店を選ぶコンポーネント
 */
function Selection(props) {
  const [dataLists, setDataLists] = useState({
    "topDataList":initDataList,
    "standbyDataList":null,
  })
  let hiddenDataList = null
  let isLoading = false

  // APIからお店のデータを得る
  const getInfo = (newUserId, newGroupId, type="init", topDataList=null) => {
    if (isLoading) return;
    // if(dataList!==initDataList && !isPreloading) setDataList(initDataList)
    isLoading = true

    // ユーザID を設定
    let userId = newUserId
    if (newUserId === undefined || newUserId === null || newUserId.length === 0) {
      userId = props.userId
    }
    // グループID を設定
    let groupId = newGroupId
    if (newGroupId === undefined || newGroupId === null || newGroupId.length === 0) {
      groupId = props.groupId
    }
    const paramsId = { "user_id": userId, "group_id": groupId }
    const params = {
      ...paramsId, ...props.paramsForSearch,
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
            getInfo(null,null,"standby",newDataList)
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
    getInfo()
    // Mount 時にだけ呼び出す
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // APIにキープ・リジェクトを送信する
  const sendFeeling = (feeling, restaurant_id) => {
    axios.post('/api/feeling', {
      params: {
        user_id: props.userId,
        restaurant_id: restaurant_id,
        feeling: feeling,
      }
    })
      .then(function (response) {
        console.log(response)
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
  // Home コンポーネント から受け取った turnMode を
  // ButtonToChangeMode 用に加工
  const turnMode = () => {
    // データリストの取得待ちであることを明示する
    setDataLists({
      "topDataList":initDataList,
      "standbyDataList":null,
    })
    // モード切り替え
    props.turnMode()
  }

  let renderButtonToChangeMode = () =>{
    return (
      <ButtonToChangeMode
        mode={props.mode}
        turnMode={turnMode}
        setUserId={props.setUserId}
        setGroupId={props.setGroupId}
        produceId={props.produceId}
        getInfo={getInfo}
      />
    )
  }

  let renderButtonToInvite = () =>{
    return (
      <ButtonToInvite
        url={props.inviteUrl}
        groupId={props.groupId} 
        callInviteUrl={props.callInviteUrl}
      />
    )
  }

  let renderStandbyRestaurantInformation = () =>{
    if(dataLists.standbyDataList===null) return null
    return (
      <RestaurantInformation 
        data={dataLists.standbyDataList[0]}
        wrapperStyle={wrapperStyle}
        keep={()=>{ console.log("pushed")}}
        reject={()=>{console.log("pushed")}}
      />
    )
  }

  let renderRestaurantInformationDeck = () =>{
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
      />
    )
  }

  const display_style = 
    (props.mode==="Alone")? {display:"none"}: null

  return (
    <div className="Selection-wrapper">
      <div className="Selection-header">
        <div className={"Selection-header-content"}
          style={display_style}>
          {/* <div className="group-id">
            ルームID:{props.groupId}
          </div> */}
        </div>
      </div>
      <div className="Selection" id={"selection"}>
        { renderStandbyRestaurantInformation() }
          {/* <RestaurantInformation data={dataList[idx]} wrapperStyle={wrapperStyle} /> */}
        { renderRestaurantInformationDeck() }
        { renderButtonToInvite() }
      </div>
    </div>
  )
}

export default Selection
