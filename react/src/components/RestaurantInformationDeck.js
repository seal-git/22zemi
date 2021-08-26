import React from 'react'
// パッケージからインポート
import { useEffect } from 'react'
import { useSprings, animated, to as interpolate } from '@react-spring/web'
import { useDrag } from 'react-use-gesture'
// 他ファイルからインポート
import RestaurantInformation from './RestaurantInformation'

// カードのスタイル
var wrapperStyle = {
  margin: 0,
}

// カードの高さを指定する
function getAdaptiveStyle() {
    // let height = window.innerHeight
    let height = document.getElementById("selection").getBoundingClientRect().height
    let wrapperStyle = {
        height: height,
    }
    return wrapperStyle
};

//windowサイズの変更検知のイベントハンドラを設定
window.addEventListener('load', () => {
    wrapperStyle = getAdaptiveStyle()
})

// お店ごとに swipe カードを生成して積むコンポーネント
export default function RestaurantInformationDeck (props) {
    // 開始地点のプロパティを与えるための関数
    const from = i => {
        return {
            x:0,
            y:0,
            scale:1,
            rot:0,
            visibility:'hidden',
        }
    }
    // 移動先のプロパティを与えるための関数
    const to = i => {
        return {
            x:0,
            y:0,
            scale:1,
            rot:0,
            visibility:'visible',
        }
    }
    // スワイプ済みカードを管理するセット
    const gone = new Set()

    // スワイプ操作をハンドルする関数
    const handleLeftScreen = (dir, restaurant_id) => {
        if (dir === 'right') {
            props.keep(restaurant_id)
        } else {
            props.reject(restaurant_id)
        }
        // スワイプしきったらカードを更新
        if(gone.size===props.dataList.length){
            setTimeout( ()=>{
                props.getInfo()
            }, 1000 )
        }
    }
    // アニメーションの管理オブジェクト
    const [springProps, api] = useSprings(
      props.dataList.length,
      i => ({
        from: from(i),
        to: to(i),
      })
    )
    // 形状変換
    const trans = (s) => `scale(${s})`

    // ドラッグ時のアニメーション
    const bind = useDrag( 
      ({ args: [index], down, movement: [mx], direction: [xDir], velocity }) => {
        const trigger = velocity > 0.2
        const dir = xDir < 0 ? -1 : 1
        if(!down && trigger && props.hasRestaurant){
          gone.add(index)
        }
        api.start(i => {
          if(index !== i) return;
          const isGone = gone.has(index)
          if(isGone){
            setTimeout( () => {
                    handleLeftScreen(dir>0?'right':'left', props.dataList[i].Restaurant_id  ) 
                }
                ,500)
          }
          const x = isGone ? (200 + window.innerWidth) * dir : down ? mx: 0
          const scale = down ? 1.01 : 1
          return {
            x,
            rot: undefined,
            scale: scale,
            delay: undefined,
            config: { friction: 100, tension: down? 800: isGone ? 700 : 500 },
          }
        })
      }
    )
    // データ更新時の挙動
    useEffect(() => {
        api.start(i=>({
            from: from(i),
            to: to(i),
        }))
        // api は必ずあるはず
        // eslint-disable-next-line react-hooks/exhaustive-deps
    },props.dataList)

    // アニメーション付きのカードを描画
    return (springProps.map(({x,y,scale,rot,delay},i) => {
      return (
        <animated.div key={i} style={{x,y}}>
          <animated.div 
            {...bind(i) }
            style = { {
              transform: interpolate([scale],trans),
            }}
          >
            <RestaurantInformation data={props.dataList[i]} wrapperStyle={wrapperStyle}/>
          </animated.div>
        </animated.div>
      )
    }))
}