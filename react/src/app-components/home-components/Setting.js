import React from 'react'
import './../../css/Setting.css'
/*
 設定画面のコンポーネント
 */
function Setting(props) {
    // 「選ぶ」画面に進む処理
    const proceedToSelection = (newMode, groupId) => {
        // 検索条件を取得
        const area = document.getElementById("inputArea").value
        const genre = document.getElementById("inputGenre").value
        const maxprice = document.getElementById("inputMaxPrice").value
        const time = document.getElementById("inputTime").value
        console.log(area, genre, maxprice, time)

        // パラメータを更新
        props.setParamsForSearch({
            "place": area,
            "genre": genre,
            "maxprice": maxprice,
            "open_hour_str": time
        })

        // 新規セッションを作成
        props.setUserId(props.produceId())
        let newGroupId = groupId
        if (groupId === undefined || groupId == null || groupId.length === 0) {
            newGroupId = props.produceId()
        }
        props.setGroupId(newGroupId)

        // 招待URLを更新
        props.callInviteUrl(newGroupId)

        // モード設定
        props.setMode(newMode)

        //　チュートリアルをオンにする
        props.setTutorialIsOn(true)

        // Selection に移る
        props.setView("Selection")
    }

    return (
        <div className="setting">
            <div class="title-wrapper">
                {/* <img
                    src={Logo}
                    className={"title-image"}
                    alt={"title"} /> */}
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
                                    placeholder="新宿"
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
                                    placeholder="中華料理"
                                />
                            </div>
                        </div>
                    </div>
                    <div className="form-content-wrapper">
                        <div className="form-content">
                            <div className="form-title">
                                予算
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
                                    value="12:00"
                                    type="time"
                                />
                            </div>
                        </div>
                    </div>
                </div>
                <div class="buttons-wrapper">
                    <button className="button-alone" onClick={() => {
                        proceedToSelection("Alone", "")
                    }}>
                        <strong>
                            みんなを招待する
                        </strong>
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Setting;
