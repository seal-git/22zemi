import React from 'react'
// パッケージからインポート
import { makeStyles, withStyles } from '@material-ui/core/styles'
import Card from '@material-ui/core/Card'
import { Chip } from '@material-ui/core'
import Typography from '@material-ui/core/Typography'
// 他ファイルからインポート
import Buttons from './Buttons'

const useStyles = makeStyles((theme) => ({
    RestaurantInformation :{
        backgroundColor: 'transparent',
        height: '100%',
        width: '100%',
        margin: '3px',
        position: 'absolute',
        webkitUserSelect: 'none',
        mozUserSelect: 'none',
            MsUserSelect: 'none',
                userSelect: 'none',
    },
    cardRoot: {
        height: '99%',
        width: '98%',
        right: '0',
        left: '0',
        top: '0',
        bottom: '0',
        margin: 'auto',
        boxSizing: "border-box",
        borderRadius: '30px',
        position: 'absolute',
    },
    textPrimary: {
        fontSize: '2rem',
        fontWeight: 'bold',
        whiteSpace: 'pre-wrap',
        color: 'white',
    },
    textSecondary: {
        fontSize: '1rem',
        color: 'white',
        display: 'flex',
        whiteSpace: 'pre-line',
    },
    textStars: {
        color: 'white',
        display: 'inline-block',
        width: '40%',
    },
    space: {
        display: 'inline-block',
        margin: '0',
    },
    imageContainer :{
        position: 'absolute',
        width: '100%',
        height: '100%',
    },
    image :{
        height: '100%',
        objectFit: 'cover',
        webkitUserSelect: 'none',
        mozUserSelect: 'none',
            MsUserSelect: 'none',
                userSelect: 'none',
        pointerEvents: 'none',
    },
    imageFilter :{
        width: '100%',
        height: '100%',
        position: 'absolute',
        background: `linear-gradient( rgba(0, 0, 0, 0), rgba(0, 0, 0, 0) 70%,rgba(0, 0, 0, 1) 85%, rgba(0, 0, 0, 1))`,
    },
    cardContentWrapper :{
        height: 'auto',
        width: '100%',
        position: 'absolute',
        bottom: '15%',
    },
    tagsContainer: {
        display: 'flex',
        flexWrap: 'wrap',
        alignContent: 'space-evenly',
    }
}));

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

/*
 キープ/リジェクト画面にてお店の情報 1件を表示するコンポーネント
 */
function RestaurantInformation(props) {
    const classes = useStyles(props)
    const space = <span className={classes.space}>　</span>

    // お店画像の描画
    const renderImages = (images,restaurant_id) =>{
        return(
            <div className={classes.imageContainer}>
                <img src={images[0]} alt="restaurant-image" className={classes.image} />
            </div>
        )
    }

    const isNotEmpty = (str) =>{
        return str!==undefined && str!==null && str!==""
    }

    // お店情報の描画
    const renderCardContent = (data) =>{
        return (
            <div className={classes.cardContentWrapper}>
                <Typography className={classes.textPrimary}>
                    {data.Name}
                </Typography>
                {space}
                <Typography >
                    {isNotEmpty(data.ReviewRating)
                    ?<StyledChipRating label={data.ReviewRating} />
                    :null}
                </Typography>
                {space}
                <Typography className={classes.tagsContainer}>
                    {isNotEmpty(data.Category)? <StyledChipTag label={data.Category} />: null }
                    {isNotEmpty(data.Price)?<StyledChipTag label={'~\xA5'+data.Price} />:null}
                    {isNotEmpty(data.BusinessHour)?<StyledChipTag label={data.BusinessHour} />:null}
                    {isNotEmpty(data.Distance)?<StyledChipTag label={data.Distance} />:null}
                </Typography>
            </div>
        )
    }

    // Keep/Rejectボタンの描画
    const renderButtons = () => {
        return (
            <Buttons 
                keep={props.keep}
                reject={props.reject}
            />
        )
    }

    return (
        <div className={classes.RestaurantInformation} style={props.wrapperStyle}>
            <Card variant="outlined" className={classes.cardRoot}>
                {renderImages(props.data.Images,props.data.restaurant_id)}
                <div className={classes.imageFilter} />
                {renderCardContent(props.data)}
                {renderButtons()}
            </Card>
        </div>
    )
}

export default RestaurantInformation
