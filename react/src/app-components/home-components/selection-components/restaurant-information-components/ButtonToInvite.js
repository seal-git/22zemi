import React from 'react'
// パッケージからインポート
import { useState } from 'react'
import Dialog from '@material-ui/core/Dialog'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText';
import DialogTitle from '@material-ui/core/DialogTitle'
import { makeStyles,withStyles } from '@material-ui/core/styles'
// 他ファイルからインポート
import InviteIcon from './../../../../icon/InviteIcon'
import InviteModal from './InviteModal'
/*
招待ボタン：押すと招待URLが表示される
 */

const useStyles = makeStyles({
    ButtonToInviteContainer:{
        position: 'absolute',
        top: '35%',
        width: '100%',
        textAlign: 'right',
        pointerEvents: 'none',
        backgroundColor: 'transparent',
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
    const classes = useStyles()

    const handleClickOpen = () => {
        setOpen(true)
    };

    const handleClose = () => {
        setOpen(false)
    };

    const StyledInviteIcon = withStyles( (theme) => ({
        root:{
            width: '15%',
            height: 'auto',
            margin: '2% 2%',
            cursor: 'pointer',
            pointerEvents: 'auto',
            opacity: '.88',
            filter: 'drop-shadow(0 0 1rem black)',
        }
    }))(InviteIcon);

    const url = "https://localhost?group_id="+props.groupId
    return (
        <div className={classes.ButtonToInviteContainer}>
            <StyledInviteIcon onClick={()=>{handleClickOpen()}} />
            <InviteModal 
                open = {open}
                handleClose = {handleClose}
                url = {url}
            />
        </div>
    )
}

export default ButtonToInvite
