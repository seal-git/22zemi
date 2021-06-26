import "./ButtonToChangeMode.css";
import ButtonNowAlone from "./button_now_alone.png";
import ButtonNowGroup from "./button_now_group.png";


import React, {useRef} from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import {Paper} from "@material-ui/core";
import {makeStyles} from '@material-ui/core/styles';

/*
「ひとりで」モードから「みんなで」モードに移るボタン
 */
function ButtonToChangeMode(props) {
    const [open, setOpen] = React.useState(false);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    const group_id = useRef('');

    const enterGroup = () => {
        console.log("enter group "+group_id.current.value);
        handleClose();
        props.setMode("Group");
        props.getInfo();
    };

    const createGroup = () => {
        console.log("create group!");
        handleClose();
        props.setMode("Group");
        props.getInfo();
    }

    const leaveGroup = () => {
        console.log("leave group!");
        handleClose();
        props.setMode("Alone");
        props.getInfo();
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
                                id="group_id"
                                label="グループID"
                                variant="outlined"
                                InputLabelProps={{style:{fontSize: 12}}}
                                inputRef={group_id}/>
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
    }
}

export default ButtonToChangeMode;