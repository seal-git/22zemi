import React from 'react';
import { useEffect, useState } from "react";
import Buttons from "./Buttons";
import RestaurantInformation from "./RestaurantInformation";
import ButtonToChangeMode from "./ButtonToChangeMode";
import ButtonToInvite from "./ButtonToInvite";
import axios from "axios";
import "./Selection.css";
import TinderCard from 'react-tinder-card';
import noImageIcon from "./no_image.png";
import { assignNumGlobal } from './global';
import Credit from "./Credit";
import sampledata from "./sampleData.json"

// スワイプでお店を選ぶ画面

const initDataList = [{
  "Name": "Loading...",
  "Images": [noImageIcon, noImageIcon],
  "Price": ""
}];
const emptyDataList = [{
  "Name": "No Data:\n検索条件を変えてみてください",
  "Images": [noImageIcon, noImageIcon]
}];

var wrapperStyle = {
  margin: 0,
};

function Selection(props) {
  const [dataList, setDataList] = useState(initDataList)
  let cardNum = dataList.length
  let isLoading = false

  // APIからお店のデータを得る
  const getInfo = (newUserId, newGroupId) => {
    if (isLoading) return;
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
    const paramsId = { "user_id": userId, "group_id": groupId };
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
        cardNum = dataList.length
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

  // 初レンダリング時に自動でデータを得る
  useEffect(() => {
    getInfo()
  }, [])

  // カードをめくる
  const turnCard = () => {
    // データリストが初期状態の場合何もしない
    if (dataList[0].Name == initDataList[0].Name) return;
    // カード枚数を1減らす
    cardNum -= 1
    if (cardNum == 0) {
      // データリストの取得待ちであることを明示する
      cardNum = 1
      setDataList(initDataList)
      // リスト取得
      getInfo()
    }
  }

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
        turnCard()
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
    cardNum = 1
    setDataList(initDataList)
    // モード切り替え
    props.turnMode()
  }

  // カードの高さを指定する
  function getAdaptiveStyle() {
    let height = window.innerHeight;
    height = document.getElementById("selection").getBoundingClientRect().height;
    let wrapperStyle = {
      // backgroundColor: 'transparent', // 描画ずれを回避するため色をつける
      backgroundColor: 'white',
      height: height,
      width: '100%',
      margin: '3px',
      position: 'absolute',
    };
    return wrapperStyle;
  };
  //windowサイズの変更検知のイベントハンドラを設定
  window.addEventListener('load', () => {
    wrapperStyle = getAdaptiveStyle();
  });

  // swipe 操作をハンドル
  const handleLeftScreen = (dir, restaurant_id) => {
    console.log(dir)
    if (dir === 'right') {
      keep(restaurant_id)
    } else {
      reject(restaurant_id)
    }
  }
  const CardsContainer = (props) => {
    // スワイプできない方向を設定
    let prevents = ['up', 'down']
    if (props.dataList === initDataList || props.dataList == emptyDataList) {
      prevents = ['up', 'down', 'right', 'left']
    }
    // お店ごとに情報カードを生成
    // TinderCard として扱うことでスワイプを可能にしている
    return (props.dataList.reverse().map((data) => {
      return (
        <TinderCard
          onCardLeftScreen={(dir) => {
            handleLeftScreen(dir, data.Restaurant_id);
          }}
          preventSwipe={prevents}
          className={'tinder-ui'}
        >
          <RestaurantInformation data={data}
            wrapperStyle={wrapperStyle} />
        </TinderCard>
      );
    }))
  }
  var display_style;
  props.mode == "Alone" ? display_style = { display: "none" } : display_style = null;

  return (
    <div className="Selection-wrapper">
      <ButtonToChangeMode
        mode={props.mode}
        turnMode={turnMode}
        setUserId={props.setUserId}
        setGroupId={props.setGroupId}
        produceId={props.produceId}
        getInfo={getInfo}
      />
      <div className="Selection-header">
        <div className={"Selection-header-content"}
          style={display_style}>
          <ButtonToInvite
            url={props.inviteUrl}
            groupId={props.groupId} 
            callInviteUrl={props.callInviteUrl}
            />
          <div className="group-id">
            ルームID:{props.groupId}
          </div>
        </div>
      </div>
      <div className="Selection" id={"selection"}>
        {/* <RestaurantInformation data={dataList[idx]} wrapperStyle={wrapperStyle} /> */}
        <div className='card-container'>
          <CardsContainer dataList={dataList} />
        </div>
        {/* <Buttons reject={reject} keep={keep} /> */}{/*ボタンを取り付けようとすると工数が激増する。一旦保留*/}
      </div>
      <Credit />
    </div>

  );
}

export default Selection;
