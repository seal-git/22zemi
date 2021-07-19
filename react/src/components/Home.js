import React from 'react';
import { useState, useContext } from "react"
import { makeStyles } from '@material-ui/core/styles';
import AppBottomNavigation from "./AppBottomNavigation"
import KeepList from "./KeepList"
import Selection from "./Selection"
import Setting from "./Setting"
import "./Home.css"
import Credit from "./Credit";
import axios from "axios";
import { useHistory, useLocation } from 'react-router-dom'

const produceId = () => {
    // return Math.random().toString(32).substring(2)
    var digit = 6; //桁数
    var nines = '';
    var zeros = '';
    for(var i=0; i<digit; i++){
        nines += '9';
        zeros += '0';
    }
    var Id = Math.floor(Math.random() * Number(nines) + 1);
    Id = (zeros+Id).slice(-6);
    return Id;
}

// 現在時刻を文字列で取得
const getCurrentTime = () => {
  const date = new Date()
  const time = ('00' + date.getHours().toString()).slice(-2) + ':' + ('00'+date.getMinutes().toString()).slice(-2)
  console.log(time)
  return time
}


// ベースコンポーネントとして使う
function Home(props) {
    // view を抱える。背景操作の都合で mode は上位コンポーネント App に持たせる
    const [view, setView] = useState("Selection")
    // ユーザID、グループIDを抱える。現状自前で用意しているがAPIに要求できるほうが嬉しい
    const [userId, setUserId] = useState(produceId())

    // 招待URLの処理
    const location = useLocation()
    console.log(location)
    let invitedGroupId = location.search.slice(10)
    let initGroupId = produceId()
    const history = useHistory()
    if(invitedGroupId!==undefined && invitedGroupId!==null && invitedGroupId.length>0){
        initGroupId = invitedGroupId
        props.setMode("Group")
        history.replace('/')
    }
    
    const [groupId, setGroupId] = useState(initGroupId)
    const [paramsForSearch, setParamsForSearch] = useState(
        {"place":"新宿",
        "genre":"",
        "open_hour_str":getCurrentTime()}
    )        
    //グループID作成時に招待urをセットする
    const [inviteUrl, setInviteUrl] = useState("")

    // const createNewSession = (groupId) => {
    //     // userID はモードが変わるごとに作り直す？
    //     setUserId(produceId())

    //     // groupId が指定されていない場合システム側で用意する
    //     // 指定されている場合はそのIDを使う
    //     if (groupId === undefined || groupId === "") {
    //         groupId = produceId();
    //     }
    //     setGroupId(groupId)
    //     setInviteUrl(callInviteUrl(groupId));
    // }

    const turnMode = () => {
        // mode を反転させる
        if (props.mode === "Group") {
            props.setMode('Alone')
        } else if (props.mode === "Alone") {
            props.setMode('Group')
        } else {
            console.log("Home:turnMode:undefined mode")
            return;
        }
    };
    // 招待URLを取得
    const callInviteUrl = (groupId) => {
        const params = {group_id: groupId, }
        console.log('params',params)
        //postになったら実装
        axios.post('/api/invite', {
            params: params
        })
            .then((response) => {
                console.log(response)
                const newInviteUrl = response.data.Url
                setInviteUrl(newInviteUrl)
                console.log('new_inviteUrl',newInviteUrl)
                console.log('set_inviteUrl',inviteUrl)
            })
            .catch((error) => {
                console.log("error:", error);
            });
    }

    return (
        <div className="Home">
            <div className="Content-wrapper">
                <div className="Content">
                    {view === "Selection" ?
                        <Selection
                            mode={props.mode}
                            turnMode={turnMode}
                            userId={userId}
                            groupId={groupId}
                            setUserId={setUserId}
                            setGroupId={setGroupId}
                            produceId={produceId}
                            inviteUrl={inviteUrl}
                            callInviteUrl={callInviteUrl}
                            paramsForSearch={paramsForSearch}
                            inviteUrl={props.inviteUrl}
                        />
                        : view === "KeepList" ? 
                        <KeepList
                            mode={props.mode}
                            userId={userId}
                            groupId={groupId}
                        />
                        :
                        <Setting
                            mode={props.mode}
                            setMode={props.setMode}
                            setView={setView}
                            setUserId={setUserId}
                            setGroupId={setGroupId}
                            produceId={produceId}
                            callInviteUrl={callInviteUrl}
                            paramsForSearch={paramsForSearch}
                            setParamsForSearch={setParamsForSearch}
                        />}
                </div>
            </div>
            <AppBottomNavigation view={view} setView={setView} />
        </div>
    );
}

export default Home;