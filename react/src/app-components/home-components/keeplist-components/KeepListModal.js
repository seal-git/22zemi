import React from 'react'
// パッケージからインポート
import { useEffect, useState, useRef } from "react"
import { makeStyles, withStyles } from '@material-ui/core/styles'
import Box from '@material-ui/core/Box'
import Chip from '@material-ui/core/Chip';
import Card from '@material-ui/core/Card'
import CardMedia from '@material-ui/core/CardMedia'
import { Typography } from '@material-ui/core';

const useStyles = makeStyles((theme) => ({
    wrapper: {
        height: '100%',
        width: '100%',
        backgroundColor: '#0006',
        position: 'relative',
        inset: '0',
        margin: 'auto',
        zIndex: '10',
    },
    modal: {
        height: '92%',
        width: '95%',
        borderRadius: '15px',
        backgroundColor: 'white',
        fontFamily: 'roboto',
        fontWeight: 700,
        position: 'absolute',
        inset: '0',
        margin: 'auto',
        zIndex: '10',
    },
    modalContent: {
        overflowY: "scroll",
        height: "100%",
        '&::-webkit-scrollbar': {
            display: 'none'
        }
    },
    modalText: {
        padding: "0 6px",
    },
    media: {
        height: '130px',
        borderRadius: '15px 15px 0 0',
    },
    closeBtn: {
        margin: '0 auto',
        width: '55px',
        lineHeight: '15px',
        textAlign: 'center',
        fontWeight: "700",
        fontFamily: "Roboto",
        fontSize: "11px",
        padding: "1px 2px",
        backgroundColor: "#D90060",
        color: "#ffffff",
        border: "none",
        borderRadius: "4px",
        alignItems: "center",
        cursor: "pointer",
    },
    closeBtnWrapper: {
        width: '100%',
        // height: '25px',
        padding: "20px 0 5px",
        position: 'absolute',
        bottom: 0,
        background: 'linear-gradient(#ffffff00 , #fff 17px)',
    }
}));


/*
キープしたお店の一覧を表示するコンポーネント
 */
function KeepListModal(props) {

    const classes = useStyles();

    const StyledChipRating = withStyles({
        root: {
            backgroundColor: '#FFAD0D',
            color: 'white',
            fontSize: '1rem',
        }
    })(Chip);
    const StyledChipTag = withStyles({
        root: {
            backgroundColor: '#FF7474',
            color: 'white',
            fontSize: '1rem',
        }
    })(Chip);

    const onCloseBtnClicked = () => {
        console.log('modal close!')
        props.onClick();
    }
    return (
        <div className={classes.wrapper}  >
            <Card className={classes.modal}>
                <div className={classes.modalContent}>
                    <CardMedia
                        className={classes.media}
                        image="https://thumb.photo-ac.com/3d/3d0a74fabc7dfa20c50ef766bf733f45_w.jpeg"
                        title="tempImg"
                    />
                    <div className={classes.modalText}>


                        <p>{props.data.Name}</p>
                        <StyledChipRating label={'★' + props.data.ReviewRating} /><br />
                        <StyledChipTag label={props.data.Category} />
                        <StyledChipTag label={'¥' + props.data.Price} />
                        <StyledChipTag label={props.data.BusinessHour} />
                        <StyledChipTag label={props.data.Distance} />
                        <p>コメントやレビューを表示する。下にスクロールしていけば無限に見ることができる。ゆくゆくはいいね機能、コメント投稿機能、画像付きコメント投稿機能、コメントのいいね数に応じたランク機能、ヤフーロコやGoogleMapへの同時投稿機能、コメントの通報機能、投稿のミュート機能、長いコメントの折り畳み機能、コメントを自然言語処理でジャンル分けする機能、いいねしたコメントに似たコメントを上位表示する機能、TwitterやTiktokへのリンクをクリックするとそれぞれのアプリが開く機能、またはアプリ内ブラウザで閲覧できる機能、コメントの翻訳機能、スパムコメントを自動検出する機能、コメントの中に広告をはさむ機能、お店の公式コメントをトップ表示する機能、地図のリンク機能、タグ機能、インフルエンサーのアカウントに公式マークが表示される機能、コメントを逐次的に読み込んで負荷を減らす機能、コメントへのリプライ機能、コメントの中に予約リンクをはさむ機能、コメントの中にUberリンクをはさむ機能、コメント・クーポン・予約リンクの各タブでそれぞれ閲覧できる機能、高評価コメント・低評価コメントでそれぞれタブ分けして閲覧できる機能、コメントと星を表示する機能、コンテントを検索できる機能などを追加していきたいと考えている</p>
                        <p>{props.data.Address}</p>
                        <p>{props.data.CatchCopy}</p>
                        <p>{props.data.BusinessHour}</p>
                        <p>{props.data.Address}</p>
                        <p>{props.data.BusinessHour}</p>
                        <p>{props.data.Address}</p>
                        ここからTypography
                        <Typography>{props.data.BusinessHour}</Typography>
                        <Typography>{props.data.Address}</Typography>
                        <Typography>{props.data.BusinessHour}</Typography>
                        <Typography>{props.data.Address}</Typography>
                        <Typography>{props.data.BusinessHour}</Typography>
                        <Typography>{props.data.Address}</Typography>
                        <p>　</p>
                    </div>
                </div>
                <div className={classes.closeBtnWrapper}>
                    <div className={classes.closeBtn} onClick={() => { onCloseBtnClicked() }}>閉じる</div>
                </div>
            </Card >
        </ div >
    )
}

export default KeepListModal
