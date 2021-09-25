
import React from 'react'
// パッケージからインポート
import { useState } from 'react'
import Dialog from '@material-ui/core/Dialog'
import DialogTitle from '@material-ui/core/DialogTitle'
import { makeStyles,withStyles } from '@material-ui/core/styles'
import { CopyToClipboard } from 'react-copy-to-clipboard'
import { DialogContent, Typography } from '@material-ui/core'

// 他ファイルからインポート
import { ReactComponent as CopyBefore } from '../../../../img/copy-before.svg'
import { ReactComponent as CopyAfter } from '../../../../img/copy-after.svg'

const useStyles = makeStyles({
    CopyButton:{
        width: '100%',
        border: 'none',
        padding: '0',
        backgroundColor: 'transparent',
        cursor: 'pointer',
        pointerEvents: 'auto',
    },
})

function CopyButton(props){
    const [isCopied, setIsCopied] = useState(false)
    const classes = useStyles()
    return(
        <CopyToClipboard 
            text={props.url} 
            onCopy={() => { 
                console.log(props.url); 
                setIsCopied(true);
            }} 
        >
                {isCopied ?
                    <CopyAfter className={classes.CopyButton}/>:
                    <CopyBefore className={classes.CopyButton}/>
                }
        </CopyToClipboard>
    )
}

function InviteModal(props){
    const classes = useStyles()

    const StyledDialog = withStyles( (theme) => ({
        root:{
            alignItems: 'center',
            webkitUserSelect: 'none',
            mozUserSelect: 'none',
            MsUserSelect: 'none',
            userSelect: 'none',
        },
        paper:{
            alignItems: 'left',
            borderRadius: '5%',
        }
    }))(Dialog);

    return (
        <StyledDialog 
            open={props.open}
                onClose={()=>{props.handleClose();}}
                aria-labelledby="form-dialog-title" >
            <DialogTitle id="form-dialog-title" >
                みんなを招待しよう
            </DialogTitle>
            <DialogContent>
                リンクをシェアして友達と一緒に<br />
                レストランを決めよう！
            </DialogContent>
            <DialogContent >
                <CopyButton className={classes.CopyButton} url={props.url}/>
            </DialogContent>
        </StyledDialog>
    )
}

export default InviteModal
