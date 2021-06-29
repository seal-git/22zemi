import { useEffect, useState } from "react";
import Buttons from "./Buttons";
import RestaurantInformation from "./RestaurantInformation";
import ButtonToChangeMode from "./ButtonToChangeMode";
import axios from "axios";
import "./Selection.css"

// スワイプでお店を選ぶ画面

const initDataList = [{ "Name": "Waiting...", "Images": [""] }];

var wrapperStyle = { margin: '5px 5px 5px 5px' };

function Selection(props) {
  const [idx, setIndex] = useState(0)
  const [dataList, setDataList] = useState(initDataList)
  let isLoading = false

  // APIからお店のデータを得る
  const getInfo = () => {
    if (isLoading) return;
    isLoading = true
    const params = { "user_id": props.userId, "group_id": props.groupId };
    // if (props.mode === "Group") {
    //   params["group_id"] = props.groupId
    // }
    console.log(params);
    axios.post('/api/info', {
      params: params
    })
      .then(function (response) {
        console.log(response)
        let dataList = response['data']
        console.log(dataList[0])
        setIndex(0)
        setDataList(dataList)
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
    // インデックスがリストのサイズを超えようとしてる場合何もしない
    if (idx >= dataList.length) return
    // 次のインデックスが out of range の場合新たにリストを取得する
    // range に収まる場合は カードをめくる
    const nextIdx = idx + 1
    if (nextIdx === dataList.length) {
      // データリストの取得待ちであることを明示する
      setIndex(0)
      setDataList(initDataList)
      // リスト取得
      getInfo()
    } else {
      // カードをめくる
      setIndex(nextIdx)
    }
  }

  // APIにキープ・リジェクトを送信する
  const sendFeeling = (feeling) => {
    axios.post('/api/feeling', {
      params: {
        user_id: props.userId,
        restaurant_id: dataList[idx].Restaurant_id,
        feeling: feeling,
      }
    })
      .then(function (response) {
        console.log(response)
        turnCard()
      })
      .catch((error) => {
        console.log("error:", error);
      });
  }

  // 各ボタンに対応する関数
  const reject = () => {
    console.log("reject")
    if (isLoading) return;
    sendFeeling(false)
  }
  const keep = () => {
    console.log("keep")
    if (isLoading) return;
    sendFeeling(true)
  }
  // Home コンポーネント から受け取った turnMode を
  // ButtonToChangeMode 用に加工
  const turnMode = (groupId) => {
    console.log("Selection:turnMode")
    // データリストの取得待ちであることを明示する
    setIndex(0)
    setDataList(initDataList)
    // モード切り替え
    props.turnMode(groupId)
    // リスト取得
    getInfo()
  }

  // カードの高さを指定する
  function getAdaptiveStyle() {
    let height = window.innerHeight;
    let wrapperStyle = {
      backgroundColor: 'transparent',
      margin: '5px 5px 5px 5px',
      height: height - 100 + 'px',
    };
    return wrapperStyle;
  };
  //windowサイズの変更検知のイベントハンドラを設定
  window.addEventListener('load', () => {
    wrapperStyle = getAdaptiveStyle();
  });


  return (
    <div className="Selection">
      <ButtonToChangeMode
        mode={props.mode}
        turnMode={turnMode} />
      <RestaurantInformation data={dataList[idx]} wrapperStyle={wrapperStyle} />
      <Buttons reject={reject} keep={keep} />
    </div>

  );
}

export default Selection;
