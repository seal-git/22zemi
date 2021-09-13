import React from 'react'
// パッケージからインポート
import { useState } from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import { DialogContent } from '@material-ui/core'
import { makeStyles,withStyles } from '@material-ui/core/styles'
import { ReactComponent as CommentIcon } from '../img/commentIcon.svg';
import SvgIcon from "@material-ui/core/SvgIcon";
/*
招待ボタン：押すと招待URLが表示される
 */

const MyIcon = (props) =>{
  return (
    <SvgIcon {...props}>
        <g transform="matrix(.17857 0 0 .17857 8.904 -3.6185)">
        <path d="m17.337 20.264c-37.1 0-67.2 30.1-67.2 67.2 0 37.1 30.1 67.2 67.2 67.2s67.2-30.1 67.2-67.2c0-37.1-30.1-67.2-67.2-67.2zm-1.6 96.7c-5.1 0-9.9-0.7-14.4-2.1-1.5 0.8-3.2 1.5-5 2.2-7.8 3.1-14.9 4.1-19.5 4.4 1.5-4.2 3-9.6 3.7-15.8 0.2-1.5 0.3-3 0.3-4.4-4-5.2-6.3-11.3-6.3-17.8 0-18.5 18.5-33.5 41.2-33.5 22.8 0 41.2 15 41.2 33.5 0 3.7-0.7 7.2-2.1 10.5-3.8-2.5-8.7-4-14-4-12.3 0-22.2 8.1-22.2 18.1 0 3.2 1 6.1 2.8 8.7-1.8 0-3.8 0.2-5.7 0.2zm40.8 1.6c0.3 2.8 0.9 5.2 1.6 7-2-0.1-5.2-0.6-8.7-2-0.8-0.3-1.5-0.7-2.2-1-2 0.6-4.2 0.9-6.4 0.9-10.1 0-18.4-6.7-18.4-14.9s8.2-14.9 18.4-14.9c10.1 0 18.4 6.7 18.4 14.9 0 2.9-1 5.6-2.8 7.9 0 0.7 0.1 1.4 0.1 2.1z" />
        </g>
    </SvgIcon>
  );
}

const useStyles = makeStyles({
    ButtonToShowComment:{
        position: 'relative',
        top: '50vh',
        textAlign: 'right',
        pointerEvents: 'none',
    },
    CommentIcon:{
        pointerEvents: 'auto',
    },
})

function ButtonToShowComment(props) {
    const [open, setOpen] = useState(false)
    const classes = useStyles()

    const handleClickOpen = () => {
        setOpen(true)
    };

    const handleClose = () => {
        setOpen(false)
    };

    const StyledDialog = withStyles( (theme) => ({
        root:{
            alignItems: 'center',
            webkitUserSelect: 'none',
            mozUserSelect: 'none',
            MsUserSelect: 'none',
            userSelect: 'none',
        },
    }))(Dialog);

    const StyledMyIcon = withStyles( (theme) => ({
        root:{
            height: '52px',
            width: '52px',
            cursor: 'pointer',
            margin: '10px',
            border: 'solid',
            fill:'white',
            backgroundColor: 'black',
            borderRadius: '50%',
        },
    }))(MyIcon);

    return (
        <div className={classes.ButtonToShowComment}>
                <StyledMyIcon 
                className={classes.CommentIcon} 
                onClick={handleClickOpen}
                />
            <StyledDialog open={open}
                    onClose={handleClose}
                    aria-labelledby="form-dialog-title">
                <DialogTitle >Title</DialogTitle>
                <DialogContent>Content</DialogContent>
            </StyledDialog>
        </div>
    )
}

export default ButtonToShowComment