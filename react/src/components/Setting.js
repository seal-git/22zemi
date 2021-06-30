import React from 'react';
import './Setting.css'
import { Button, Grid,FormControl,Input, Container,TextField, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/core";
import SearchButtonOne from "./search_button_one.png"
import SearchButtonAll from "./search_button_all.png"

// 現在時刻を文字列で取得
const getCurrentTime = () => {
  const date = new Date()
  const time = ('00' + date.getHours().toString()).slice(-2) + ':' + ('00'+date.getMinutes().toString()).slice(-2)
  console.log(time)
  return time
}

// 設定画面
function Setting(props) {

  // 「決める」ボタンが叩かれたときの処理
  const proceedToSelection = (newMode,groupId) => {
    // モード切り替え
    // 暫定的な処置。ポップアップなどで manage したい
    if(newMode!==props.mode){
      props.turnMode(groupId)
    }

    // 検索条件を取得
    const area = document.getElementById("inputArea").value
    const genre = document.getElementById("inputGenre").value
    const time = +document.getElementById("inputTime").value.slice(0,2) // time は int にする
    console.log(area,genre,time)

    // パラメータを更新
    // props.setParams({"area":area, "genre":genre, "time":time })

    // Selection に移る
    props.setView("Selection")
  }
  const CustomInput = (props) => {
    return(
      <Input id={props.id} defaultValue={props.defaultValue} inputProps={{ 'aria-label': 'description' }} />
    )
  }
  return (
    <div className="setting">
      <div class="box-title">
        <div class="label-title">
          <Typography>Reskima</Typography>
        </div>
      </div>
      <div class="box-area">
        <label className="label-area">
          <Typography>
            エリア
          </Typography>
        </label>
      </div>
      <div class="input-area">
        <CustomInput defaultValue="四ツ谷駅" id="inputArea"></CustomInput>
      </div>
      <div class="box-genre">
        <label className="label-genre">
          <Typography>
            ジャンル
          </Typography>
        </label>
      </div>
      <div class="input-genre">
        <CustomInput defaultValue="居酒屋" id="inputGenre"></CustomInput>
      </div>
      <div class="box-time">
        <label className="label-time">
          <Typography>
            時間
          </Typography>
        </label>
      </div>
      <TextField className="input-time" defaultValue={getCurrentTime()} type="time" id="inputTime" />
      <button className="button-alone" onClick={()=>{proceedToSelection("Alone","")}}>
        <img 
          src={SearchButtonOne}
          className={"button-alone-image"}
          alt={"ButtonAlone"} />
      </button>
      <button className="button-group" onClick={()=>{proceedToSelection("Group","")}}>
        <img 
          src={SearchButtonAll}
          className={"button-group-image"}
          alt={"ButtonGroup"} />
      </button>
    </div>
  );
}
export default Setting;
