import React from 'react'
import './css/KeepListTile.css'
// パッケージからインポート
import { Box, CardContent, Grid } from '@material-ui/core'
import { makeStyles } from '@material-ui/core/styles'
import Card from '@material-ui/core/Card'
import CardMedia from '@material-ui/core/CardMedia'
import Typography from '@material-ui/core/Typography'
import FavoriteIcon from '@material-ui/icons/Favorite'

const useStyles = makeStyles((theme) => ({
    root: {
        margin: '10px',
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
        props.onClick(props.data)
    }

    return (
        <Card className={classes.root}>

            <CardMedia
                className={classes.media}
                image="https://thumb.photo-ac.com/3d/3d0a74fabc7dfa20c50ef766bf733f45_w.jpeg"
                title="tempImg"
            />
            <CardContent class="cardContent">
                <Grid container spacing={0}>
                    <Grid item xs={12}>
                        <Typography class="textVotes"
                            style={props.mode === "Alone" ? { display: "block", } : { display: "block", }}>
                            <span class="textVoteResult">
                                <FavoriteIcon style={{ fontSize: 16, paddingRight: '5px' }} />
                                {props.data.VotesLike}
                            </span>
                            /{props.data.VotesAll}
                        </Typography>
                    </Grid>
                    <Grid item xs={8}>
                        <Grid container spacing={0}>
                            <Grid item xs={12}>
                                <Typography class="textShopName">
                                    {props.data.Name}
                                </Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography class="textSecondary">
                                    {props.data.Category}/~¥{props.data.Price}/{props.data.BusinessHour}
                                </Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography class="textSecondary">
                                    <span class="textStars">★</span>
                                    {props.data.ReviewRating}
                                </Typography>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={4}>
                        <div class="buttonWrapper">
                            <div class="buttonContainer">
                                <div class="cardAction" onClick={() => { onInfoBtnClicked() }}>詳細を見る<span class="playIcon">▶︎</span></div>
                                <div class="cardAction">予約する</div>
                            </div>
                        </div>
                    </Grid>
                </Grid>
            </CardContent>

        </Card >
    )
}

export default KeepListTile