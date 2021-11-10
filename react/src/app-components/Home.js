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

// const produceId = () => {
//     var digit = 6 //桁数
//     var nines = ''
//     var zeros = ''
//     for (var i = 0; i < digit; i++) {
//         nines += '9'
//         zeros += '0'
//     }
//     var Id = Math.floor(Math.random() * Number(nines) + 1)
//     Id = (zeros + Id).slice(-6)
//     return Id
// }

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
        const params = { group_pass_number: groupId, }
        console.log('params', params)
        axios.post('/api/init', {
            params: params
        })
            .then((response) => {
                console.log(response)
                const newUserId = response.data.UserId
                const newGroupId = response.data.GroupId
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
                            setView={setView}
                            initNewSession={initNewSession}
                            paramsForSearch={paramsForSearch}
                        />
                        : view === "Selection" ?
                        <Selection
                            inviteUrl={inviteUrl}
                            paramsForSearch={paramsForSearch}
                            tutorialIsOn={tutorialIsOn}
                            keepNumberRef={keepNumberRef}
                        />
                        : view === "KeepList" ?
                            <KeepList
                                paramsForSearch={paramsForSearch}
                                setTutorialIsOn={setTutorialIsOn}
                            />
                            :
                            <Setting
                                setView={setView}
                                paramsForSearch={paramsForSearch}
                                setParamsForSearch={setParamsForSearch}
                                setTutorialIsOn={setTutorialIsOn}
                                keepNumberRef={keepNumberRef}
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