import React from 'react'
import "./Selection.css"
// パッケージからインポート
import axios from "axios"
import { useEffect, useState } from "react"
// 他のファイルからインポート
import { assignNumGlobal } from './global'
import ButtonToChangeMode from "./ButtonToChangeMode"
import ButtonToInvite from "./ButtonToInvite"
import Credit from "./Credit"
import RestaurantInformationDeck from './RestaurantInformationDeck'
import noImageIcon from "..//img/no_image.png"

const initDataList = [{
  "Name": "Loading...",
  "Images": [noImageIcon, noImageIcon],
  "Price": ""
}]
const emptyDataList = [{
  "Name": "No Data:\n検索条件を変えてみてください",
  "Images": [noImageIcon, noImageIcon]
}]

/*
 スワイプでお店を選ぶコンポーネント
 */
function Selection(props) {
  const [dataList, setDataList] = useState(initDataList)
  let isLoading = false

  // APIからお店のデータを得る
  const getInfo = (newUserId, newGroupId) => {
    if (isLoading) return;
    if(dataList!==initDataList) setDataList(initDataList)
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
        let dataList = response['data']
        // let dataList = sampledata
        let cardNum = dataList.length
        if (cardNum > 0) {
          console.log(dataList[0])
          setDataList(dataList)
        } else {
          setDataList(emptyDataList)
        }
        isLoading = false
      })
      .catch((error) => {
        console.log("error:", error);
      });
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
        assignNumGlobal(response.data)
      })
      .catch((error) => {
        console.log("error:", error);
      });
  }

  // 各ボタンに対応する関数
  const reject = (restaurant_id) => {
    console.log("reject")
    if (isLoading) return;
    sendFeeling(false, restaurant_id)
  }
  const keep = (restaurant_id) => {
    console.log("keep:", restaurant_id)
    if (isLoading) return;
    sendFeeling(true, restaurant_id)
  }
  // Home コンポーネント から受け取った turnMode を
  // ButtonToChangeMode 用に加工
  const turnMode = () => {
    // データリストの取得待ちであることを明示する
    setDataList(initDataList)
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

  let renderRestaurantInformationDeck = () =>{
    return (
      <RestaurantInformationDeck
        dataList={dataList}
        hasRestaurant={
          dataList !== initDataList 
          && dataList !== emptyDataList}
        keep={keep}
        reject={reject}
        getInfo={getInfo}
      />
    )
  }

  var display_style;
  props.mode === "Alone" 
  ? display_style = { display: "none" } 
  : display_style = null;

  return (
    <div className="Selection-wrapper">
      { renderButtonToChangeMode() }
      <div className="Selection-header">
        <div className={"Selection-header-content"}
          style={display_style}>
          { renderButtonToInvite() }
          <div className="group-id">
            ルームID:{props.groupId}
          </div>
        </div>
      </div>
      <div className="Selection" id={"selection"}>
        <div className='information-deck'>
          {/* <RestaurantInformation data={dataList[idx]} wrapperStyle={wrapperStyle} /> */}
          { renderRestaurantInformationDeck() }
        </div>
      </div>
      <Credit />
    </div>

  );
}

export default Selection
