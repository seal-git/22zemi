import React from 'react';
import { useState } from "react"
import { makeStyles } from '@material-ui/core/styles';
import AppBottomNavigation from "./AppBottomNavigation"
import KeepList from "./KeepList"
import Selection from "./Selection"
import Setting from "./Setting"
import "./Home.css"
import Credit from "./Credit";

const produceId = () => {
    return Math.random().toString(32).substring(2)
}

// 現在時刻を文字列で取得
const getCurrentTime = () => {
    const date = new Date()
    const time = ('00' + date.getHours().toString()).slice(-2) + ':' + ('00' + date.getMinutes().toString()).slice(-2)
    console.log(time)
    return time
}

// ベースコンポーネントとして使う
function Home(props) {
    // view を抱える。背景操作の都合で mode は上位コンポーネント App に持たせる
    const [view, setView] = useState("Selection")
    // ユーザID、グループIDを抱える。現状自前で用意しているがAPIに要求できるほうが嬉しい
    const [userId, setUserId] = useState(produceId())
    const [groupId, setGroupId] = useState(produceId())
    const [paramsForSearch, setParamsForSearch] = useState(
        {
            "place": "新宿",
            "genre": "居酒屋",
            "open_hour_str": getCurrentTime()
        }
    )
    const [listNum, setListNum] = useState(0);

    const createNewSession = (groupId) => {
        // userID はモードが変わるごとに作り直す？
        setUserId(produceId())

        // groupId が指定されていない場合システム側で用意する
        // 指定されている場合はそのIDを使う
        if (groupId === undefined || groupId === "") {
            setGroupId(produceId())
        } else {
            setGroupId(groupId)
        }
    }

    const turnMode = (groupId) => {
        // mode を反転させる
        if (props.mode === "Group") {
            props.setMode('Alone')
        } else if (props.mode === "Alone") {
            props.setMode('Group')
        } else {
            console.log("Home:turnMode:undefined mode")
            return;
        }
        createNewSession(groupId);
    };


    return (
        <div className="Home">
            <div className="Content-wrapper">
                <div className="Content">
                    {view === "Selection" ?
                        <Selection
                            userId={userId}
                            groupId={groupId}
                            mode={props.mode}
                            setMode={props.setMode}
                            turnMode={turnMode}
                            paramsForSearch={paramsForSearch}
                            setListNum={setListNum}
                        />
                        : view === "KeepList" ? <KeepList
                            userId={userId}
                            groupId={groupId}
                            mode={props.mode}
                            setMode={props.setMode}
                            turnMode={turnMode}
                            setListNum={setListNum}
                        />
                            : <Setting
                                mode={props.mode}
                                setMode={props.setMode}
                                createNewSession={createNewSession}
                                setView={setView}
                                paramsForSearch={paramsForSearch}
                                setParamsForSearch={setParamsForSearch} />}
                </div>
                <Credit />
            </div>
            <AppBottomNavigation view={view} setView={setView} listNum={listNum} />
        </div>
    );
}

export default Home;