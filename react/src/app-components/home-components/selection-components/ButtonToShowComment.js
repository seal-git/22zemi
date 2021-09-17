import React from 'react'
// パッケージからインポート
import { useState } from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import { DialogContent } from '@material-ui/core'
import { makeStyles,withStyles } from '@material-ui/core/styles'
// 他ファイルからインポート
import CommentIcon from './../../../icon/CommentIcon'

/*
招待ボタン：押すと招待URLが表示される
 */


const useStyles = makeStyles({
    ButtonToShowCommentContainer:{
        position: 'absolute',
        top: '60%',
        width: '100%',
        textAlign: 'right',
        pointerEvents: 'none',
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

    const StyledCommentIcon = withStyles( (theme) => ({
        root:{
            width: '15%',
            height: 'auto',
            cursor: 'pointer',
            margin: '2% 2%',
            opacity: '0.88',
            pointerEvents: 'auto',
        },
    }))(CommentIcon);

    return (
        <div className={classes.ButtonToShowCommentContainer}>
                <StyledCommentIcon onClick={()=>{handleClickOpen()}} />
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