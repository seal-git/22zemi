import React from 'react'
import './Setting.css'
// パッケージからインポート
import { useState, useRef } from 'react'
import {
    Button,
    Dialog,
    DialogContent,
    DialogTitle,
    makeStyles,
    Paper,
    TextField,
    Typography
} from "@material-ui/core"
// 他のファイルからインポート
import { assignNumGlobal } from './global'
import Logo from "..//img/Reskima_Logo2.svg"
import SearchButtonOne from "..//img/search_button_one.png"
import SearchButtonAll from "..//img/search_button_all.png"

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
                inputProps={{ 'aria-label': 'description' }}
                variant={"outlined"}
                sx={{
                    width: 300,
                    color: 'success.main',
                }}
            />
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
                                    type="text"
                                    placeholder="4000"
                                    data-format="$1 円以内"
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
                                    placeholder="22:00"
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
                    {/* <Dialog open={open}
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
                    </Dialog> */}
                </div>
            </div>
        </div>
    );
}

export default Setting;
