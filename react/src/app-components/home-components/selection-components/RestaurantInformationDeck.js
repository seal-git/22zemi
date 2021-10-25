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
        height: '100%',
        width: '100%',
        position: 'absolute',
    }
}))

// お店ごとに swipe カードを生成して積むコンポーネント
export default function RestaurantInformationDeck(props) {
    const classes = useStyles()
    // 開始地点のプロパティを与えるための関数
    const initFrom = i => {
        return {
            x: 0,
            y: 0,
            scale: 1,
            rot: 0,
            visibility: 'hidden',
        }
    }
    // 移動先のプロパティを与えるための関数
    const initTo = i => {
        return {
            x: 0,
            y: 0,
            scale: 1,
            rot: 0,
            visibility: 'visible',
        }
    }

    // スワイプ操作時のプロパティを与える関数
    const swipeTo = (x, scale, down, isGoing) => {
        return {
            x: x,
            scale: scale,
            config: { friction: 20, tension: down ? 170 : isGoing ? 400 : 500 },
        }
    }

    // スワイプ済みカードを管理するセット
    const willGo = new Set()
    const hasGone = new Set()

    // スワイプやボタンによる選択操作をハンドルする関数
    const handleSelection = (dir, restaurant_id) => {
        if (restaurant_id === "init") return
        if (dir > 0) {
            props.keep(restaurant_id)
        } else {
            props.reject(restaurant_id)
        }
        // 選び切る前にカードを読み込み
        if (willGo.size === Math.max(props.topDataList.length - 1, 1)) {
            console.log("preloading")
            props.getInfo("preload", null)
        }

        // 選び切ったらカードを更新
        if (willGo.size === Math.max(props.topDataList.length, 1)) {
            setInterval(() => {
                props.setPreloadedDataList()
            }, 500)
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
            if (!down && trigger && props.hasRestaurant) {
                willGo.add(index)
            }
            // アニメーションの起動
            api.start(i => {
                if (index !== i) return;
                if (hasGone.has(index)) return;
                const isGoing = willGo.has(index)
                if (isGoing) {
                    setTimeout(() => {
                        handleSelection(dir, props.topDataList[i].Restaurant_id)
                    }, 400)
                    hasGone.add(index);
                }
                const x =
                    !props.hasRestaurant ? 0
                        : isGoing ? (200 + window.innerWidth) * dir
                            : down ? mx
                                : 0
                const scale = down ? 1.01 : 1
                return swipeTo(x, scale, down, isGoing)
            })
        }
    )
    // データ更新時の挙動
    useEffect(() => {
        api.start(i => ({
            from: initFrom(i),
            to: initTo(i),
        }))
        // api は必ずあるはず
        // eslint-disable-next-line react-hooks/exhaustive-deps
    })

    // Keep/Reject ボタンの共通動作
    const handlePushButton = (dir, index) => {
        // 不適な状態の場合何も行わず return
        if (!props.hasRestaurant) return
        // 選択済みインデックスのセットに index を追加
        willGo.add(index)
        // アニメーションの起動
        api.start(i => {
            if (index !== i) return
            if (hasGone.has(index)) return
            if (!willGo.has(index)) return
            hasGone.add(index)
            setTimeout(() => {
                handleSelection(dir, props.topDataList[i].Restaurant_id)
            }, 400)
            const x = (200 + window.innerWidth) * dir
            return swipeTo(x, 1, false, true)
        })
    }

    // Keepボタンの動作
    const handlePushKeepButton = (index) => {
        handlePushButton(1, index)
    }
    // Rejectボタンの動作
    const handlePushRejectButton = (index) => {
        handlePushButton(-1, index)
    }

    // お店情報の描画
    const renderRestaurantInformation = (index) => {
        return (
            <RestaurantInformation
                data={props.topDataList[index]}
                wrapperStyle={props.wrapperStyle}
                keep={() => { handlePushKeepButton(index) }}
                reject={() => { handlePushRejectButton(index) }}
                groupId={props.groupId}
                inviteUrl={props.inviteUrl}
            />
        )
    }

    const maxIndex = props.topDataList.length - 1
    // アニメーション付きのカードを描画
    return (
        <div className={classes.RestaurantInformationDeck} >
            {springProps.reverse().map(({ x, y, scale }, i) => {
                const index = maxIndex - i
                return (
                        <animated.div
                            key={'card' + props.topDataList[index].Restaurant_id}
                            style={{ x, y, 
                            height: '100%',
                            width:'100%', 
                            position: 'absolute',
                            }}>
                            <animated.div
                                {...bind(index)}
                                style={{
                                    transform: interpolate([scale], trans),
                                    height: '100%',
                                    width: '100%',
                                }}
                            >
                                {renderRestaurantInformation(index)}
                            </animated.div>
                        </animated.div>
                )
            })}
        </div>
    )
}