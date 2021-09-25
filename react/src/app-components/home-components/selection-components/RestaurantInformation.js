import React from 'react'
// パッケージからインポート
import { useState, useEffect } from 'react'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import Card from '@material-ui/core/Card'
import { Chip } from '@material-ui/core'
import Typography from '@material-ui/core/Typography'
import Box from '@material-ui/core/Box'
// 他ファイルからインポート
import Buttons from './restaurant-information-components/Buttons'
import ButtonToShowComment from './restaurant-information-components/ButtonToShowComment'
import ButtonToInvite from './restaurant-information-components/ButtonToInvite'
import ImageArea from './restaurant-information-components/ImageArea'

const useStyles = makeStyles((theme) => ({
    RestaurantInformation :{
        backgroundColor: 'transparent',
        height: '70%',
        width: '100%',
        margin: '.5%',
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
        borderRadius: '5%',
        position: 'absolute',
        color: 'transparent',
    },
    textPrimary: {
        fontSize: '2rem',
        fontWeight: 'bold',
        whiteSpace: 'pre-wrap',
        color: 'white',
        filter: 'drop-shadow(0 0 0.3rem black)',
    },
    space: {
        display: 'inline-block',
        margin: '0',
    },
}));


const StyledChipRating = withStyles({
    root: {
        backgroundColor: '#FFAD0D',
        color: 'white',
        fontSize: '1.5rem',
    }
})(Chip);
const StyledChipTag = withStyles({
    root: {
        backgroundColor: '#D90060',
        height: '10%',
        color: 'white',
        fontSize: '1.5rem',
    }
})(Chip);

/*
 キープ/リジェクト画面にてお店の情報 1件を表示するコンポーネント
 */
function RestaurantInformation(props) {
    const classes = useStyles(props)
    const space = <span className={classes.space}>　</span>

   // 画像の描画
   const renderImageArea = (data) =>{
       return(
           <ImageArea 
                Images={data.Images}
                restaurant_id={data.Restaurant_id}
           />
       )
   }

    // お店情報の描画
    const isNotEmpty = (str) =>{
        return str!==undefined && str!==null && str!==""
    }
    const renderCardContent = (data) =>{
        return (
            <Box
                height='auto'
                width='100%'
                position='absolute'
                bottom='15%'
            >
                <Typography className={classes.textPrimary}>
                    {data.Name}
                </Typography>
                <Typography >
                    {isNotEmpty(data.ReviewRating)
                    ?<StyledChipRating label={data.ReviewRating} />
                    :null}
                </Typography>
                <Box 
                    display='flex'
                    flexWrap='wrap'
                    alignContent='space-evenly'
                >
                    {isNotEmpty(data.Category)? <StyledChipTag label={data.Category} />: null }
                    {isNotEmpty(data.Price)?<StyledChipTag label={'~\xA5'+data.Price} />:null}
                    {isNotEmpty(data.BusinessHour)?<StyledChipTag label={data.BusinessHour} />:null}
                    {isNotEmpty(data.Distance)?<StyledChipTag label={data.Distance} />:null}
                </Box>
            </Box>
        )
    }
    // 招待ボタンの描画
    let renderButtonToInvite = () =>{
        return (
        <ButtonToInvite
            url={props.inviteUrl}
            groupId={props.groupId} 
            callInviteUrl={props.callInviteUrl}
        />
        )
    }
    // コメントボタンの描画
    const renderButtonToShowComment = () =>{
        const ok = props.data.Restaurant_id !== 'init' 
            && props.data.Restaurant_id !== 'empty' 
            && props.data.Restaurant_id.indexOf('tutorial')==-1

        return (
            ok
            ?<ButtonToShowComment data={props.data} />
            :null
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
                {renderImageArea(props.data)}
                {renderCardContent(props.data)}
                {renderButtons()}
                {renderButtonToInvite()}
                {renderButtonToShowComment()}
            </Card>
        </div>
    )
}

export default RestaurantInformation