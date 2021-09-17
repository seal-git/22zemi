import React from 'react'
// パッケージからインポート
import { useState } from 'react'
import Dialog from '@material-ui/core/Dialog'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText';
import DialogTitle from '@material-ui/core/DialogTitle'
import { makeStyles,withStyles } from '@material-ui/core/styles'
import { CopyToClipboard } from 'react-copy-to-clipboard'
// 他ファイルからインポート
import InviteIcon from './../../../icon/InviteIcon'
/*
招待ボタン：押すと招待URLが表示される
 */

const useStyles = makeStyles({
    ButtonToInviteContainer:{
        position: 'absolute',
        top: '50%',
        width: '100%',
        textAlign: 'right',
        pointerEvents: 'none',
    },
    CopyButton:{
        height: '100%',
        width: '40%',
        border: 'none',
        padding: '0',
        color: 'white',
        backgroundColor: '#ff7474',
        borderRadius: '9px',
        cursor: 'pointer',
        pointerEvents: 'auto',
    }
})

function ButtonToInvite(props) {
    const [open, setOpen] = useState(false)
    const [isCopied, setIsCopied] = useState(false)
    const classes = useStyles()

    const handleClickOpen = () => {
        setOpen(true)
        setIsCopied(false)
    };

    const handleClose = () => {
        setOpen(false)
    };

    const StyledInviteIcon = withStyles( (theme) => ({
        root:{
            width: '15%',
            height: 'auto',
            margin: '2% 2%',
            opacity: '0.88',
            cursor: 'pointer',
            pointerEvents: 'auto',
        }
    }))(InviteIcon);

    const StyledDialog = withStyles( (theme) => ({
        root:{
            alignItems: 'center',
            webkitUserSelect: 'none',
            mozUserSelect: 'none',
            MsUserSelect: 'none',
            userSelect: 'none',
        },
    }))(Dialog);


    const url = "https://localhost?group_id="+props.groupId
    return (
        <div className={classes.ButtonToInviteContainer}>
            <StyledInviteIcon onClick={()=>{handleClickOpen()}} />
            <StyledDialog open={open}
                    onClose={handleClose}
                    aria-labelledby="form-dialog-title">
                <DialogTitle id="form-dialog-title">
                    みんなを招待しよう
                </DialogTitle>
                <List>
                    <ListItem>
                        <ListItemText>
                            リンクをシェアして友達と一緒にレストランを決めよう！
                        </ListItemText>
                    </ListItem>
                    <ListItem>
                        <CopyToClipboard text={url} onCopy={()=>{setIsCopied(true)}}>
                            <button className={classes.CopyButton}>
                                {isCopied?
                                <div>コピー成功!</div>:
                                <div>URLをコピーする</div>}
                            </button>
                        </CopyToClipboard>
                    </ListItem>
                </List>
            </StyledDialog>
        </div>
    )
}

export default ButtonToInvite