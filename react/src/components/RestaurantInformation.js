import React from 'react'
// パッケージからインポート
import { useState, useEffect } from 'react'
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
        backgroundColor: 'transparent',
    },
    image :{
        height: '100%',
        objectFit: 'cover',
        backgroundColor: 'transparent',
        webkitUserSelect: 'none',
        mozUserSelect: 'none',
        MsUserSelect: 'none',
        userSelect: 'none',
        pointerEvents: 'none',
        willChange: 'opacity',
        position: 'absolute',
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
    },
    imageBarContainer:{
        width: '80%',
        height: '10px',
        top: '5%',
        left: '10%',
        display: 'flex',
        position: 'absolute',
    },
    imageBarSelected :{
        height: '100%',
        width: '100%',
        background: 'rgba(255,255,255,1)',
        boxShadow: '0px 4px 4px rgba(0, 0, 0, 0.75)',
        border: '2px solid gray',
        borderRadius: '10%',
        margin: '1%',
        cursor: 'pointer',
    },
    imageBar :{
        height: '100%',
        width: '100%',
        background: 'rgba(0,0,0,0.4)',
        boxShadow: '0px 4px 4px rgba(0, 0, 0, 0.75)',
        border: '2px solid gray',
        borderRadius: '10%',
        margin: '1%',
        cursor: 'pointer',
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
        backgroundColor: '#D90060',
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

    const [index, setIndex] = useState(0)

    const renderBars = () => {
        return(
            <div className={classes.imageBarContainer}>
                {props.data.Images.map( (image,i) =>{
                    return <div 
                    className={i===index?classes.imageBarSelected:classes.imageBar}
                    onClick={()=>{ setIndex(i)}}
                    />
                })} 
            </div>
        )
    }

    useEffect(() => {
        const currentIndex = index
        const t = setInterval(
            () => {
                if(currentIndex!==undefined && currentIndex===index){
                    setIndex(state => (state + 1) % props.data.Images.length)
                }
            }
        , 5000)
        return ()=>{clearInterval(t)}
    },[index])

    // お店画像の描画
    const renderImages = (restaurant_id) =>{
        return(
            <div className={classes.imageContainer}>
                {props.data.Images.map( (image,i)=>{
                    return <img 
                        className={classes.image}
                        id={restaurant_id+'-image'+i}
                        alt={'restaurant-image'+i}
                        src={image} 
                        style={{opacity: index===i?1:0, transition:'0.5s',}}
                    />
                  })}
            </div>
        )
    }


    // お店情報の描画
    const isNotEmpty = (str) =>{
        return str!==undefined && str!==null && str!==""
    }
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
                {renderImages(props.data.restaurant_id)}
                <div className={classes.imageFilter} />
                {renderCardContent(props.data)}
                {renderButtons()}
                {renderBars()}
            </Card>
        </div>
    )
}

export default RestaurantInformation