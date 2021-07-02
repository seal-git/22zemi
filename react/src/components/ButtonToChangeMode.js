import React from 'react';
import "./ButtonToChangeMode.css";
import ButtonNowAlone from "./button_now_alone.png";
import ButtonNowGroup from "./button_now_group.png";


import {useState, useRef} from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import {Paper} from "@material-ui/core";
import {makeStyles} from '@material-ui/core/styles';
import { assignNumGlobal } from './global';

/*
「ひとりで」モードから「みんなで」モードに移るボタン
 */
function ButtonToChangeMode(props) {
    const [open, setOpen] = useState(false);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const groupIdRef = useRef("");

    const setNewIds = (groupId) => {
        // ユーザID を設定
        let newUserId = props.produceId()
        props.setUserId(newUserId)

        let newGroupId = groupId
        // グループIDを設定
        if(newGroupId===undefined || newGroupId===null || newGroupId.length===0){
            newGroupId = props.produceId()
        }
        props.setGroupId(newGroupId)
        return [newUserId, newGroupId]
    }

    const enterGroup = () => {
        handleClose();

        // ID の再設定
        let [newUserId,newGroupId] = setNewIds(groupIdRef.current.value)
        console.log("enter group ",newGroupId)

        // 招待URLを設定
        // props.callInviteUrl(newGroupId)
         
        // モード切り替え
        props.turnMode()
        // カード枚数表示を0にする
        assignNumGlobal(0)
        // 情報取り直し
        props.getInfo(newUserId, newGroupId)
    };

    const createGroup = () => {
        handleClose();

        // ID を再設定
        let [newUserId,newGroupId] = setNewIds()
        console.log("create group ",newGroupId);
        // 招待URLを設定
        // props.callInviteUrl(newGroupId)
        // モード切り替え
        props.turnMode()
        // カード枚数表示を0にする
        assignNumGlobal(0)
        // 情報取り直し
        props.getInfo(newUserId, newGroupId)
    }

    const leaveGroup = () => {
        handleClose();
        // ID を再設定
        let [newUserId,newGroupId] = setNewIds()
        console.log("leave group to group ",newGroupId);

        // 招待URLを設定
        // props.setInviteUrl(props.callInviteUrl(newGroupId))
        // モード切り替え
        props.turnMode()
        // カード枚数表示を0にする
        assignNumGlobal(0)

        // 情報取り直し
        props.getInfo(newUserId, newGroupId)
    }

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

    if (props.mode == "Alone") {
        return (
            <div className="ButtonToChangeMode">
                <button className={"button-to-change-mode"}
                        onClick={handleClickOpen}>
                    <img src={ButtonNowAlone}
                         className={"button-icon"}
                         alt={"ButtonIcon"}/>
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
                                id="groupIdRef"
                                label="グループID"
                                variant="outlined"
                                InputLabelProps={{style:{fontSize: 12}}}
                                inputRef={groupIdRef}/>
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
    } else if (props.mode == "Group") {
        return (
            <div className="ButtonToChangeMode">
                <button className={"button-to-change-mode"}
                        onClick={handleClickOpen}>
                    <img src={ButtonNowGroup}
                         className={"button-icon"}
                         alt={"ButtonIcon"}/>
                </button>
                <Dialog open={open}
                        onClose={handleClose}
                        aria-labelledby="dialog-title">
                    <DialogContent>
                        この部屋から退室してひとりで選びますか？
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={handleClose} color="primary">
                            いいえ
                        </Button>
                        <Button onClick={leaveGroup} color="primary">
                            退室
                        </Button>
                    </DialogActions>
                </Dialog>
            </div>
        );
    }else{
        return(<div><h1>error</h1></div>);
    }
}

export default ButtonToChangeMode;