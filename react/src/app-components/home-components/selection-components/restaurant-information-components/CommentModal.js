
import React from 'react'
// パッケージからインポート
import { makeStyles, withStyles } from '@material-ui/core/styles'
import Chip from '@material-ui/core/Chip';
import { Box, Dialog, DialogContent, DialogContentText, DialogTitle } from '@material-ui/core';
import { Slide } from '@material-ui/core';
// 他ファイルからインポート
import { ReactComponent as CommentClose } from '../../../../img/comment-close.svg';

// モーダルの遷移方法を規定する
const Transition = React.forwardRef(function Transition(props, ref) {
    return <Slide direction="up" ref={ref} {...props} />;
});

const useStyles = makeStyles((theme) => ({
    CommentModal: {
        webkitUserSelect: 'none',
        mozUserSelect: 'none',
        MsUserSelect: 'none',
        userSelect: 'none',
    },
    CommentCloseButton: {
        width: '5%',
        paddingTop: '4%',
        paddingRight: '4%',
        cursor: 'pointer',
    },
    textShopName: {
        padding: "0 16px",
        margin: "0",
        fontSize: "1.5rem",
        fontWeight: "700"
    },
    textSecondary: {
        fontWeight: "700",
        padding: "6px 0 0 0",
        margin: "0",
        fontSize: "1rem",
        whiteSpace: "pre-line",
        color: 'black'
    },
}));

/*
 コメントモーダルの本体を描画するコンポーネント
*/
function CommentModal(props) {
    const classes = useStyles();
    // レーティングを表示するためのチップ
    const StyledChipRating = withStyles({
        root: {
            backgroundColor: '#FFAD0D',
            color: 'white',
            fontSize: '1rem',
            margin: '2px'
        }
    })(Chip);
    // タグ情報を表示するためのチップ
    const StyledChipTag = withStyles({
        root: {
            backgroundColor: '#D90060',
            color: 'white',
            fontSize: '1rem',
            margin: '2px'
        }
    })(Chip);

    // 空文字を確認する関数
    const isNotEmpty = (str) => {
        return str !== undefined && str !== null && str !== ""
    }
    // レーティングチップの描画
    const renderChipRating = (rate) => {
        return (
            isNotEmpty(rate)
                ? <div>
                    <StyledChipRating label={'★' + rate} />
                </div>
                : null
        )
    }
    // タグチップの描画
    const renderChipTags = (data) => {
        return (
            <div>
                {isNotEmpty(data.Distance) ? <StyledChipTag label={data.Distance} /> : null}
                {isNotEmpty(data.Price) ? <StyledChipTag label={'~\xA5' + data.Price} /> : null}
                {isNotEmpty(data.Category) ? <StyledChipTag label={data.Category} /> : null}
                {isNotEmpty(data.BusinessHour) ? <StyledChipTag label={data.BusinessHour} /> : null}
            </div>
        )
    }

    return (
        <Dialog
            open={props.open}
            onClose={props.handleClose}
            TransitionComponent={Transition}
            scroll='body'
            className={classes.CommentModal}
            // style={{ backgroundColor: 'yellow', padding: '40px' }}
            fullWidth={true}
        >
            <Box
                textAlign="right"
            >
                <CommentClose className={classes.CommentCloseButton} onClick={props.handleClose} />
            </Box>
            {props.showPicture != undefined && props.showPicture != null && props.showPicture
                ?
                // <div style={{ height: '50%' }}>
                //     <ImageArea
                //         Images={props.data.Images}
                //         restaurant_id={props.data.Restaurant_id}
                //     />
                // </div>
                null
                : null
            }
            {/* <DialogTitle>
            </DialogTitle> */}
            <p className={classes.textShopName}>{props.data.Name}</p>
            <DialogContent>
                {renderChipRating(props.data.ReviewRating)}
                {renderChipTags(props.data)}
                <DialogContentText>
                    <div className={classes.textSecondary}>
                        {props.data.Address}
                    </div>

                    <div className={classes.textSecondary}>
                        {props.data.CatchCopy}
                    </div>

                </DialogContentText>
            </DialogContent>
        </ Dialog >
    )
}

export default CommentModal
