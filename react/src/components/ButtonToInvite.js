import React from 'react';

import {useState, useRef} from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import {Paper} from "@material-ui/core";
import {makeStyles, withStyles} from '@material-ui/core/styles';

/*
招待ボタン：押すと招待URLが表示される
 */

function ButtonToInvite(props) {
    const [open, setOpen] = useState(false);

    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };



    const MyButton = withStyles((theme) => ({
    root: {
        height: '30px',
        background: 'linear-gradient(116.73deg,' +
            ' #FFCD4E 27.25%,' +
            ' #FFB74A' +
            ' 71.71%)',
        margin: '5px',
        border: '0px',
        fontSize: '0.8rem',
    }
}))(Button);


    return (
        <div className="ButtonToInvite">
            <MyButton className={"button-to-invite"}
                    onClick={handleClickOpen}>
                    招待
            </MyButton>
            <Dialog open={open}
                    onClose={handleClose}
                    aria-labelledby="form-dialog-title">
                <DialogTitle id="form-dialog-title">
                    招待URL
                </DialogTitle>
                <DialogContent>
                    {props.url}
                </DialogContent>
            </Dialog>
        </div>
    )
}

export default ButtonToInvite;