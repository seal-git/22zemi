import React from 'react'
// パッケージからインポート
import { makeStyles } from '@material-ui/core'
import { useEffect } from 'react'
import { useSprings, animated, to as interpolate } from '@react-spring/web'
import { useDrag } from 'react-use-gesture'
// 他ファイルからインポート
import RestaurantInformation from './RestaurantInformation'

const useStyles = makeStyles((theme) => ({
  RestaurantInformationDeck: {
    position:'relative',
  }
}))

// お店ごとに swipe カードを生成して積むコンポーネント
export default function RestaurantInformationDeck (props) {
    const classes = useStyles()
    // 開始地点のプロパティを与えるための関数
    const initFrom = i => {
        return {
            x:0,
            y:0,
            scale:1,
            rot:0,
            visibility:'hidden',
        }
    }
    // 移動先のプロパティを与えるための関数
    const initTo = i => {
        return {
            x:0,
            y:0,
            scale:1,
            rot:0,
            visibility:'visible',
        }
    }

    // スワイプ操作時のプロパティを与える関数
    const swipeTo = (x,scale,down,isGone) =>{
        return {
            x: x,
            scale: scale,
            config: { friction: 20, tension: down? 170: isGone ? 400 : 500 },
        }
    }

    // スワイプ済みカードを管理するセット
    const gone = new Set()

    // スワイプやボタンによる選択操作をハンドルする関数
    const handleSelection = (dir, restaurant_id) => {
        if (restaurant_id==="init") return
        if (dir>0) {
            props.keep(restaurant_id)
        } else {
            props.reject(restaurant_id)
        }
        // 選び切る前にカードを読み込み
        if(gone.size===Math.max(props.topDataList.length-1,1)){
            console.log("preloading")
            props.getInfo(null,null,"preload",null)
        }

        // 選び切ったらカードを更新
        if(gone.size===Math.max(props.topDataList.length,1)){
            setInterval( ()=>{
                props.setPreloadedDataList() 
            }, 500 )
        }
    }
    // アニメーションの管理オブジェクト
    const [springProps, api] = useSprings(
      props.topDataList.length,
      i => ({
        from: initFrom(i),
        to: initTo(i),
      })
    )
    // 形状変換
    const trans = (s) => `scale(${s})`

    // ドラッグ時のアニメーション
    const bind = useDrag( 
      ({ args: [index], down, movement: [mx], direction: [xDir], velocity }) => {
        // ドロップする直前のドラッグの勢いを選択のトリガーとする
        const trigger = velocity > 0.2
        // ドラッグの方向. Keep/Reject の判断にも使う
        const dir = xDir < 0 ? -1 : 1
        // 選択が行われた場合選択済みインデックスセットに index を追加する
        if(!down && trigger && props.hasRestaurant){
          gone.add(index)
        }
        // アニメーションの起動
        api.start(i => {
          if(index !== i) return;
          const isGone = gone.has(index)
          if(isGone){
            setTimeout( () => {
                    handleSelection(dir, props.topDataList[i].Restaurant_id  ) 
                },400)
          }
          const x = 
            !props.hasRestaurant? 0
            : isGone ? (200 + window.innerWidth) * dir 
            : down ? mx
            : 0
          const scale = down ? 1.01 : 1
          return swipeTo(x,scale,down,isGone)
        })
      }
    )
    // データ更新時の挙動
    useEffect(() => {
        api.start(i=>({
            from: initFrom(i),
            to: initTo(i),
        }))
        // api は必ずあるはず
        // eslint-disable-next-line react-hooks/exhaustive-deps
    },)

    // Keep/Reject ボタンの共通動作
    const handlePushButton = (dir,index) =>{
      // 不適な状態の場合何も行わず return
      if(!props.hasRestaurant) return
      // 選択済みインデックスのセットに index を追加
      gone.add(index)
      // アニメーションの起動
      api.start(i => {
        if(index!==i) return
        if(!gone.has(index)) return
        setTimeout( ()=> {
          handleSelection(dir,props.topDataList[i].Restaurant_id)
        },400)
        const x = (200 + window.innerWidth) * dir
        return swipeTo(x,1,false,true)
      })
    }

    // Keepボタンの動作
    const handlePushKeepButton = (index) =>{
      handlePushButton(1,index)
    }
    // Rejectボタンの動作
    const handlePushRejectButton = (index) =>{
      handlePushButton(-1,index)
    }

    // お店情報の描画
    const renderRestaurantInformation = (index) =>{
      return(
        <RestaurantInformation
          data={props.topDataList[index]}
          wrapperStyle={props.wrapperStyle}
          keep={() => { handlePushKeepButton(index) }}
          reject={() => { handlePushRejectButton(index) }}
        />
      )
    }

    const maxIndex = props.topDataList.length - 1
    // アニメーション付きのカードを描画
    return (
      <div>
        {springProps.reverse().map(({x,y,scale},i) => {
          const index = maxIndex - i
          return (
            <div className={classes.RestaurantInformationDeck}>
              <animated.div 
                key={'card'+props.topDataList[index].Restaurant_id} 
                style={{x,y}}>
                <animated.div 
                  {...bind(index) }
                  style = { {
                    transform: interpolate([scale],trans),
                  }}
                >
                  {renderRestaurantInformation(index)}
                </animated.div>
              </animated.div>
            </div>
          )
        })}
      </div>
    )
}