import React from 'react';
import { useState, useRef } from 'react';
import './Setting.css'
import {
    Button,
    Dialog,
    DialogContent,
    DialogTitle,
    Paper,
    Grid,
    FormControl,
    Input,
    Container,
    TextField,
    Typography
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core";
import Logo from "./Reskima_Logo.png"
import SearchButtonOne from "./search_button_one.png"
import SearchButtonAll from "./search_button_all.png"
import { assignNumGlobal } from './global'

// 設定画面
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

        // カード枚数表示を0にする
        assignNumGlobal(0)

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
        console.log("enter group " + group_id.current.value);
        handleClose();
        proceedToSelection('Group', group_id.current.value)
    };
    const createGroup = () => {
        console.log("create group!");
        handleClose();
        proceedToSelection('Group', "")
    }

    // フォーム
    const CustomInput = (props) => {
        return (
            <TextField id={props.id}
                defaultValue={props.defaultValue}
                inputProps={{ 'aria-label': 'description' }} />
        )
    }
    return (
        <div className="setting">
            <div class="title-wrapper">
                <img
                    src={Logo}
                    className={"title-image"}
                    alt={"title"} />
            </div>
            <div class="forms-wrapper">
                <div class="form-content-wrapper">
                    <div class="form-content">
                        <div className="form-title">
                            <Typography>
                                エリア
                            </Typography>
                        </div>
                        <CustomInput
                            defaultValue={props.paramsForSearch['place']}
                            id="inputArea"></CustomInput>
                    </div>
                </div>
                <div className="form-content-wrapper">
                    <div className="form-content">
                        <div className="form-title">
                            <Typography>
                                ジャンル
                            </Typography>
                        </div>
                        <div className="input-genre">
                            <CustomInput
                                defaultValue={props.paramsForSearch['genre']}
                                id="inputGenre"></CustomInput>
                        </div>
                    </div>
                </div>
                <div className="form-content-wrapper">
                    <div className="form-content">
                        <div className="form-title">
                            <Typography>
                                予算
                            </Typography>
                        </div>
                        <div className="input-genre">
                            <CustomInput
                                defaultValue={props.paramsForSearch['maxprice']}
                                id="inputMaxPrice"></CustomInput>
                            円以内
                        </div>
                    </div>
                </div>
                <div className="form-content-wrapper">
                    <div className="form-content">
                        <div className="form-title">
                            <Typography>
                                時間
                            </Typography>
                        </div>
                        <div className="input-time">
                            <TextField
                                defaultValue={props.paramsForSearch['open_hour_str']}
                                type="time" id="inputTime" />
                        </div>
                    </div>
                </div>
            </div>
            <div class="buttons-wrapper">
                <button className="button-alone" onClick={() => {
                    proceedToSelection("Alone", "")
                }}>
                    <img
                        //buttonのstyleはここで指定しないと描画がずれる
                        src={SearchButtonOne}
                        className={"button-alone-image"}
                        width={"auto"}
                        alt={"ButtonAlone"}/>
                </button>
                <button className="button-group" onClick={() => {
                    handleClickOpen("")
                }}>
                    <img
                        //buttonのstyleはここで指定しないと描画がずれる
                        src={SearchButtonAll}
                        className={"button-group-image"}
                        width={"auto"}
                        alt={"ButtonGroup"}/>
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
        </div>
    );
}

export default Setting;
