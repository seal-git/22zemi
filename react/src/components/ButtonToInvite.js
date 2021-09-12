import React from 'react'
// パッケージからインポート
import { useState } from 'react'
import Button from '@material-ui/core/Button'
import Dialog from '@material-ui/core/Dialog'
import DialogContent from '@material-ui/core/DialogContent'
import DialogTitle from '@material-ui/core/DialogTitle'
import { withStyles } from '@material-ui/core/styles'
import { CopyToClipboard } from 'react-copy-to-clipboard'

/*
招待ボタン：押すと招待URLが表示される
 */
function ButtonToInvite(props) {
    const [open, setOpen] = useState(false)
    const [isCopied, setIsCopied] = useState(false)

    const handleClickOpen = () => {
        setOpen(true)
        setIsCopied(false)
    };

    const handleClose = () => {
        setOpen(false)
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

    const url = "https://reskima.com?group_id="+props.groupId
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
                    {url} 
                </DialogContent>
                    <CopyToClipboard text={url} onCopy={()=>{setIsCopied(true)}}>
                        <Button variant='contained' color='primary'>
                            {isCopied?
                            <div>URLをコピーしました!</div>:
                            <div>URLをコピーする</div>}
                        </Button>
                    </CopyToClipboard>
            </Dialog>
        </div>
    )
}

export default ButtonToInvite