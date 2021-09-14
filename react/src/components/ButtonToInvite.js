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
import PersonAddIcon from '@material-ui/icons/PersonAdd';
/*
招待ボタン：押すと招待URLが表示される
 */

const useStyles = makeStyles({
    ButtonToInvite:{
        position: 'relative',
        top: '50vh',
        textAlign: 'right',
        pointerEvents: 'none',
    },
    ModalButton:{
        height: '60px',
        width: '60px',
        borderRadius: '50%',
        backgroundColor: 'white',
        cursor: 'pointer',
        margin: '10px',
        border: 'solid',
        pointerEvents: 'auto',
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

    const StyledDialog = withStyles( (theme) => ({
        root:{
            alignItems: 'center',
            webkitUserSelect: 'none',
            mozUserSelect: 'none',
            MsUserSelect: 'none',
            userSelect: 'none',
        },
    }))(Dialog);

    const StyledPersonAddIcon = withStyles( (theme) => ({
        root:{
            transform: 'scale(-1,1)',
        }
    }))(PersonAddIcon);

    const url = "https://localhost?group_id="+props.groupId
    return (
        <div className={classes.ButtonToInvite}>
            <button 
                className={classes.ModalButton}
                onClick={handleClickOpen}>
                    <StyledPersonAddIcon fontSize='large'/>
            </button>
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