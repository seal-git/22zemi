import React, { useEffect, useRef } from 'react'
import './../../css/Setting.css'
/*
 設定画面のコンポーネント
 */

const getCurrentTime = () =>{
    const date = new Date(Date.now())
    const h = date.getHours()
    const m = date.getMinutes()
    return h + ":" + m
}

function Setting(props) {
    let timeRef = useRef(null)
    // 「選ぶ」画面に進む処理
    const proceedToSelection = () => {
        // 検索条件を取得
        let area = document.getElementById("inputArea").value
        let genre = document.getElementById("inputGenre").value
        let maxprice = document.getElementById("inputMaxPrice").value
        let time = document.getElementById("inputTime").value
        console.log(area, genre, maxprice, time)

        // パラメータを更新
        if (area==="" && genre==="" && maxprice==="" && time===""){
            time = getCurrentTime()
        }
        props.setParamsForSearch({
            "place": area,
            "genre": genre,
            "maxprice": maxprice,
            "open_hour_str": time
        })

        //　チュートリアルをオフにする
        props.setTutorialIsOn(false)

        // StartingSession に移る
        props.setView("StartingSession")
    }

    useEffect(() => {
        timeRef.current.value = getCurrentTime()
        // Mount 時にだけ呼び出す
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    return (
        <div className="setting">
            <div class="title-wrapper">
            </div>
            <div class="setting-wrapper">
                <div class="forms-wrapper">
                    <div class="form-label">
                        <strong>
                            条件を決める
                        </strong>
                    </div>
                    <div class="form-content-wrapper">
                        <div class="form-content">
                            <div class="form-title">
                                エリア
                            </div>
                            <div class="input-wrapper">
                                <input
                                    id="inputArea"
                                    placeholder="例：新宿"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="form-content-wrapper">
                        <div className="form-content">
                            <div className="form-title">
                                ジャンル
                            </div>
                            <div>
                                <input
                                    id="inputGenre"
                                    placeholder="例：中華料理"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="form-content-wrapper">
                        <div className="form-content">
                            <div className="form-title">
                                予算（円）
                            </div>
                            <div>
                                <input
                                    id="inputMaxPrice"
                                    type="text"
                                    placeholder="4000"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="form-content-wrapper">
                        <div className="form-content">
                            <div className="form-title">
                                入店時間
                            </div>
                            <div>
                                <input
                                    id="inputTime"
                                    type="time"
                                    ref={timeRef}
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <div class="buttons-wrapper">
                    <button className="button-alone" onClick={() => {
                        proceedToSelection("")
                    }}>
                        <strong>
                            お店を選ぶ
                        </strong>
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Setting;
