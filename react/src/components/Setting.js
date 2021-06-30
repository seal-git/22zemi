import React from 'react';
import { useState,useRef } from 'react';
import './Setting.css'
import { Button, Dialog, DialogContent,DialogTitle, Paper, Grid,FormControl,Input, Container,TextField, Typography } from "@material-ui/core";
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
  // 「選ぶ」画面に進む処理
  const proceedToSelection = (newMode,groupId) => {
    // 検索条件を取得
    const area = document.getElementById("inputArea").value
    const genre = document.getElementById("inputGenre").value
    const time = +document.getElementById("inputTime").value.slice(0,2) // time は int にする
    console.log(area,genre,time)

    // パラメータを更新
    props.setParamsForSearch({"place":area, "genre":genre, "open_hour":time })

    // モード切り替え
    props.setMode(newMode)

    // 新規セッションを作成
    props.createNewSession(groupId)

    // Selection に移る
    props.setView("Selection")
  }

  // ポップアップ関連の設定
  const useStyles = makeStyles((theme) => ({
      root: {
          '& .MuiTextField-root': {
              margin: theme.spacing(0),
              width: '14ch',
              height: '2ch',
              padding: '0',
          },
          '& .MuiOutlinedInput-input': {
              padding: '8px',
              height: '2ch'
          }
      },
  }));
  const classes = useStyles();

  // ポップアップ制御
  const [open, setOpen] = useState(false);
  const handleClickOpen = () => {
      setOpen(true);
  };
  const handleClose = () => {
      setOpen(false);
  };
  const group_id = useRef("");
  const enterGroup = () => {
      console.log("enter group "+group_id.current.value);
      handleClose();
      proceedToSelection('Group',group_id.current.value)
  };
  const createGroup = () => {
      console.log("create group!");
      handleClose();
      proceedToSelection('Group',"")
  }

  // フォーム
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
      <button className="button-group" onClick={()=>{handleClickOpen("")}}>
        <img 
          src={SearchButtonAll}
          className={"button-group-image"}
          alt={"ButtonGroup"} />
      </button>
      <Dialog open={open}
        onClose={handleClose}
        aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">
          グループで選ぶ
        </DialogTitle>
        <DialogContent>
          <Paper className={classes.root}>
            <TextField
              id="group_id"
              label="グループID"
              variant="outlined"
              InputLabelProps={{ style: { fontSize: 12 } }}
              inputRef={group_id} />
            <Button onClick={enterGroup}
              variant="contained"
              color="primary"
              height="100%">
              入室
            </Button>
          </Paper>
          <div>
            <Button onClick={createGroup}
              color="secondary"
              variant="contained">
              ルームを新規作成
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
export default Setting;
