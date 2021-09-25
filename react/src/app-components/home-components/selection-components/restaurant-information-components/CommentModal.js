
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
        }
    })(Chip);
    // タグ情報を表示するためのチップ
    const StyledChipTag = withStyles({
        root: {
            backgroundColor: '#D90060',
            color: 'white',
            fontSize: '1rem',
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
                ? <DialogContent>
                    <StyledChipRating label={'★' + rate} />
                </DialogContent>
                : null
        )
    }
    // タグチップの描画
    const renderChipTags = (data) => {
        return (
            <DialogContent>
                {isNotEmpty(data.Category) ? <StyledChipTag label={data.Category} /> : null}
                {isNotEmpty(data.Price) ? <StyledChipTag label={'~\xA5' + data.Price} /> : null}
                {isNotEmpty(data.BusinessHour) ? <StyledChipTag label={data.BusinessHour} /> : null}
                {isNotEmpty(data.Distance) ? <StyledChipTag label={data.Distance} /> : null}
            </DialogContent>
        )
    }

    return (
        <Dialog
            open={props.open}
            onClose={props.handleClose}
            TransitionComponent={Transition}
            scroll='body'
            className={classes.CommentModal}
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
            <DialogTitle>
                {props.data.Name}
            </DialogTitle>
            {renderChipRating(props.data.ReviewRating)}
            {renderChipTags(props.data)}
            <DialogContent>
                <DialogContentText>
                    コメントやレビューを表示する。下にスクロールしていけば無限に見ることができる。ゆくゆくはいいね機能、コメント投稿機能、画像付きコメント投稿機能、コメントのいいね数に応じたランク機能、ヤフーロコやGoogleMapへの同時投稿機能、コメントの通報機能、投稿のミュート機能、長いコメントの折り畳み機能、コメントを自然言語処理でジャンル分けする機能、いいねしたコメントに似たコメントを上位表示する機能、TwitterやTiktokへのリンクをクリックするとそれぞれのアプリが開く機能、またはアプリ内ブラウザで閲覧できる機能、コメントの翻訳機能、スパムコメントを自動検出する機能、コメントの中に広告をはさむ機能、お店の公式コメントをトップ表示する機能、地図のリンク機能、タグ機能、インフルエンサーのアカウントに公式マークが表示される機能、コメントを逐次的に読み込んで負荷を減らす機能、コメントへのリプライ機能、コメントの中に予約リンクをはさむ機能、コメントの中にUberリンクをはさむ機能、コメント・クーポン・予約リンクの各タブでそれぞれ閲覧できる機能、高評価コメント・低評価コメントでそれぞれタブ分けして閲覧できる機能、コメントと星を表示する機能、コンテントを検索できる機能などを追加していきたいと考えている<br />
                    {props.data.Address}<br />
                    {props.data.CatchCopy}<br />
                    {props.data.BusinessHour}<br />
                    {props.data.Address}<br />
                    {props.data.BusinessHour}<br />
                    {props.data.Address}<br />
                    {props.data.BusinessHour}<br />
                    {props.data.Address}<br />
                    {props.data.BusinessHour}<br />
                    {props.data.Address}<br />
                    {props.data.BusinessHour}<br />
                    {props.data.Address}<br />
                </DialogContentText>
            </DialogContent>
        </ Dialog >
    )
}

export default CommentModal
