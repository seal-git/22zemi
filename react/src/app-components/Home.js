import React, { useEffect } from 'react'
import "./../css/Home.css"
// パッケージからインポート
import axios from "axios"
import { useState, useRef } from "react"
import { useHistory, useLocation } from 'react-router-dom'
// 他のファイルからインポート
import AppBottomNavigation from "./home-components/AppBottomNavigation"
import StartingSession from './home-components/StartingSession'
import KeepList from "./home-components/KeepList"
import Selection from "./home-components/Selection"
import Setting from "./home-components/Setting"

// 現在時刻を文字列で取得
const getCurrentTime = () => {
    const date = new Date()
    const time = ('00' + date.getHours().toString()).slice(-2) + ':' + ('00' + date.getMinutes().toString()).slice(-2)
    console.log(time)
    return time
}

/*
 メイン画面を統括するコンポーネント
 */
function Home(props) {
    const [view, setView] = useState("StartingSession")
    const [tutorialIsOn,setTutorialIsOn] = useState(true)
    const keepNumberRef = useRef(null);

    // 招待URLの処理
    const location = useLocation()
    console.log(location)
    let invitedGroupId = location.search.slice(10)
    let initGroupId = ""
    const history = useHistory()
    if (invitedGroupId !== undefined && invitedGroupId !== null && invitedGroupId.length > 0) {
        initGroupId = invitedGroupId
        history.replace('/')
    }

    const [paramsForSearch, setParamsForSearch] = useState(
        {
            "user_id":"",
            "group_id":initGroupId,
            "place": "新宿",
            "genre": "",
            "open_hour_str": getCurrentTime()
        }
    )
    //グループID作成時に招待urlをセットする
    const [inviteUrl, setInviteUrl] = useState("")

    const initNewSession =  () => {
        console.log("init New Session")
        const groupId = paramsForSearch["group_id"]
        const params = { group_id: groupId, }
        console.log('params', params)
        axios.post('/api/init', {
            params: params
        })
            .then((response) => {
                console.log(response)
                const newUserId = response.data.UserId
                const newGroupId = groupId===""?response.data.GroupId:groupId
                const params = { group_id: newGroupId, }
                axios.post('api/invite', {
                    params: params,
                })
                    .then( (response) =>{
                        console.log(response)
                        const newInviteUrl = response.data.Url
                        const newParamsForSearch = {...paramsForSearch, user_id:newUserId, group_id:newGroupId, }
                        console.log(newParamsForSearch)
                        setInviteUrl(newInviteUrl)
                        setParamsForSearch(newParamsForSearch)
                        setView("Selection")
                    })
            })
            .catch((error) => {
                console.log("error:", error)
            });
    }

    useEffect(() => {
        keepNumberRef.current = 0
        console.log('current',keepNumberRef.current)
        // Mount 時にだけ呼び出す
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    return (
        <div className="Home">
            <div className="Screen">
            <div className="Content-wrapper">
                <div className="Content">
                    {
                        view === "StartingSession" ?
                            <StartingSession
                                initNewSession={initNewSession}
                            />
                        : view === "Selection" ?
                            <Selection
                                inviteUrl={inviteUrl}
                                keepNumberRef={keepNumberRef}
                                paramsForSearch={paramsForSearch}
                                tutorialIsOn={tutorialIsOn}
                            />
                        : view === "KeepList" ?
                            <KeepList
                                paramsForSearch={paramsForSearch}
                                setTutorialIsOn={setTutorialIsOn}
                            />
                        :
                            <Setting
                                keepNumberRef={keepNumberRef}
                                paramsForSearch={paramsForSearch}
                                setParamsForSearch={setParamsForSearch}
                                setTutorialIsOn={setTutorialIsOn}
                                setView={setView}
                            />}
                </div>
            <AppBottomNavigation 
                view={view} 
                setView={setView} 
                keepNumberRef={keepNumberRef}
            />
            </div>
            </div>
        </div>
    )
}

export default Home