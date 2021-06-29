import { useEffect, useState } from "react";
import Buttons from "./Buttons";
import RestaurantInformation from "./RestaurantInformation";
import ButtonToChangeMode from "./ButtonToChangeMode";
import axios from "axios";
import "./Selection.css"
import TinderCard from 'react-tinder-card'

// スワイプでお店を選ぶ画面

const initDataList = [{ "Name": "Waiting...", "Images": [""] }];

var wrapperStyle = { margin: '5px 5px 5px 5px' };

function Selection(props) {
  // const [idx, setIndex] = useState(0)
  var idx = 0
  const [dataList, setDataList] = useState(initDataList)
  let isLoading = false

  // APIからお店のデータを得る
  const getInfo = () => {
    if (isLoading) return;
    isLoading = true
    const params = { 
      "user_id": props.userId,
      "group_id": props.groupId,
    }
    console.log(params);
    axios.post('/api/info', {
      params: params
    })
      .then(function (response) {
        console.log(response)
        let dataList = response['data']
        console.log(dataList[0])
        // setIndex(0)
        idx = 0
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
      // setIndex(0)
      idx = 0
      setDataList(initDataList)
      // リスト取得
      getInfo()
    } else {
      // カードをめくる
      // setIndex(nextIdx)
      idx = nextIdx
    }
  }

  // APIにキープ・リジェクトを送信する
  const sendFeeling = (feeling) => {
    axios.post('/api/feeling', {
      params: {
        user_id: 1,
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
    // setIndex(0)
    idx = 0
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

  const CardsContainer = (props) => {
    if (props.dataList !== initDataList) {
      return (props.dataList.reverse().map((data) => {
        return (
          <TinderCard
            onCardLeftScreen={() => { console.log('left'); console.log(idx); keep(); }}
            preventSwipe={['up', 'down']}
          >
            <RestaurantInformation data={data} wrapperStyle={wrapperStyle} />
          </TinderCard>
        );
      })
      );
    }else{
      return(  props.dataList.reverse().map( (data)=>{
              return(
              <TinderCard
                onSwipe={() => {console.log('left');console.log(idx); turnCard(); }}
                preventSwipe={['up', 'down','right','left']}
              >
                <RestaurantInformation data={data} />
              </TinderCard>
              );
            }  )
    );
    }
  }


  return (
    <div className="Selection">
      <ButtonToChangeMode
        mode={props.mode}
        turnMode={turnMode} />
      {/* <RestaurantInformation data={dataList[idx]} wrapperStyle={wrapperStyle} /> */}
      <CardsContainer dataList={dataList} />
      <Buttons reject={reject} keep={keep} />
    </div>

  );
}

export default Selection;
