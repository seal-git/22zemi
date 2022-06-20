import React from 'react'
import './../../../css/KeepListTile.css'
// パッケージからインポート
import { Box, CardContent, Grid } from '@material-ui/core'
import { makeStyles } from '@material-ui/core/styles'
import Card from '@material-ui/core/Card'
import CardMedia from '@material-ui/core/CardMedia'
import Typography from '@material-ui/core/Typography'
import FavoriteIcon from '@material-ui/icons/Favorite'

const useStyles = makeStyles((theme) => ({
    root: {
        margin: '0px 10px 10px 10px',
        borderRadius: '10px',
    },
    media: {
        height: '130px',
    },
}));

/*
 キープしたお店の情報1件を表示するコンポーネント
 */
function KeepListTile(props) {
    const classes = useStyles()
    // const swichStyle = { props.mode == "Alone" ? { display: "none", } : { display: "block", } }

    const onInfoBtnClicked = () => {
        props.onClick(props.data);
    }

    const onReserveBtnClicked = () => {
        window.open(props.data.UrlWeb, '_blank');
    }


    return (
        <Card className={classes.root}>
            <CardMedia
                className={classes.media}
                image={props.data.Images[0]}
                title="tempImg"
            />
            <CardContent class="cardContent">
                <Grid container spacing={0}>
                    <Grid item xs={12}>
                        <Typography class="textVotes"
                            style={props.data.VotesLike > 1 ? { display: "block", } : { display: "none", }}>
                            <span class="textVoteResult">
                                <FavoriteIcon style={{ fontSize: 16, paddingRight: '5px' }} />
                                {props.data.VotesLike}
                            </span>
                            /{props.data.VotesAll}
                        </Typography>
                    </Grid>
                    <Grid item xs={12}>
                        <Grid container spacing={0}>
                            <Grid item xs={12}>
                                <Typography class="textShopName">
                                    {props.data.Name}
                                </Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography class="textSecondary">
                                    {props.data.Category != null
                                        ? <span style={{ paddingRight: '5px' }}>{props.data.Category}</span>
                                        : <span style={{ paddingRight: '5px', color: '#bbb' }}>ジャンル不明</span>}
                                    {props.data.Price != null
                                        ? <span style={{ paddingRight: '5px' }}>~¥{props.data.Price}</span>
                                        : <span style={{ paddingRight: '5px', color: '#bbb' }}>価格不明</span>}
                                    {props.data.BusinessHour != null
                                        ? <span style={{ paddingRight: '5px' }}>{props.data.BusinessHour}</span>
                                        : <span style={{ paddingRight: '5px', color: '#bbb' }}>開店時間不明</span>}
                                </Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography class="textSecondary">
                                    <span class="textStars">
                                        {props.data.ReviewRating}
                                    </span>
                                </Typography>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12}>
                        <div class="buttonWrapper">
                            <Grid class="buttonContainer" item xs={6}>
                                <div class="cardAction" onClick={() => { onReserveBtnClicked() }}>予約する</div>
                            </Grid>
                            <Grid class="buttonContainer" item xs={6}>
                                <div class="cardAction" onClick={() => { onInfoBtnClicked() }}>詳細を見る<span class="playIcon">▶︎</span></div>
                            </Grid>
                        </div>
                    </Grid>
                </Grid>
            </CardContent>

        </Card >
    )
}

export default KeepListTile