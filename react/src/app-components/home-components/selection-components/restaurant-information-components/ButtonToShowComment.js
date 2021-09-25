import React from 'react'
// パッケージからインポート
import { useState } from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import { DialogContent } from '@material-ui/core'
import { makeStyles,withStyles } from '@material-ui/core/styles'
// 他ファイルからインポート
import CommentIcon from './../../../../icon/CommentIcon'
import CommentModal from './CommentModal'

/*
招待ボタン：押すと招待リンク共有用のモーダルが開かれる
 */

const useStyles = makeStyles({
    ButtonToShowCommentContainer:{
        position: 'absolute',
        top: '46%',
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

    const StyledCommentIcon = withStyles( (theme) => ({
        root:{
            width: '15%',
            height: 'auto',
            cursor: 'pointer',
            margin: '2% 2%',
            pointerEvents: 'auto',
            opacity: '.88',
            filter: 'drop-shadow(0 0 1rem black)',
        },
    }))(CommentIcon);

    return (
        <div className={classes.ButtonToShowCommentContainer}>
            <StyledCommentIcon onClick={()=>{handleClickOpen()}} />
            <CommentModal 
                open={open}
                handleClose={handleClose}
                data={props.data}
            />
        </div>
    )
}

export default ButtonToShowComment