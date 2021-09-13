import React from 'react'
import './RestaurantInformation.css'
// パッケージからインポート
import { useRef, useEffect } from 'react'
import { CardContent } from '@material-ui/core'
import { makeStyles, withStyles } from '@material-ui/core/styles'
import Card from '@material-ui/core/Card'
import GridList from '@material-ui/core/GridList'
import GridListTile from '@material-ui/core/GridListTile'
import Typography from '@material-ui/core/Typography'
import Divider from '@material-ui/core/Divider'
import IconButton from '@material-ui/core/IconButton'
// 他ファイルからインポート
import Buttons from './Buttons'

const useStyles = makeStyles((theme) => ({
    wrapper: {
        backgroundColor: 'transparent',
        margin: '5px 5px 100px 5px',
        height: '100%',
    },
    cardRoot: {
        // marginBottom: '10px',
        height: '100%',
        boxSizing: "border-box",
        display: "flex",
        flexDirection: "column",
        borderRadius: '30px',
        position: 'relative',
    },
    gridList: {
        width: '100%',
        height: '100%',
        padding: '1px',
        overflowY: 'scroll',
    },
    gridListTile: {
    },
    cardContent: {
        width: "100%",
        boxSizing: "border-box",
        paddingBottom: "0px",
        display: 'block',
        flexWrap: 'wrap',
        justifyContent: 'space-around',
        // overflow: 'hidden',
        backgroundColor: theme.palette.background.paper,
        textAlign: 'left',
        // padding: '3px',
        // "&:last-child": {
        //   paddingBottom: '5px'
        // }
    },
    textShopName: {
        fontSize: '1.4rem',
        fontWeight: 'bold',
        whiteSpace: 'pre-wrap',
    },
    textSecondary: {
        fontSize: '1rem',
        color: '#777777',
        display: 'flex',
        whiteSpace: 'pre-line',
    },
    textStars: {
        color: '#fbc02d',
        display: 'inline-block',
        width: '40%',
    },
    space: {
        display: 'inline-block',
        margin: '0 2px',
    },
    title: {
        fontSize: 14,
    },
    pos: {
        marginBottom: 12,
    },
}));

/*
 キープ/リジェクト画面にてお店の情報 1件を表示するコンポーネント
 */
function RestaurantInformation(props) {
    const classes = useStyles()
    const space = <span className={classes.space}>　</span>
    const gl = useRef(null)

    const scroll = (stepNum, scrollStep, vector) => {
        const step = scrollStep / stepNum
        gl.current.scrollTop += vector * step
    }

    const scrollGrid = (vector) => {
        console.log(vector);
        if (gl.current.scrollHeight > gl.current.clientHeight) {
            const scrollStep = 150
            const stepNum = 20
            for (let i = 1; i <= stepNum; i++) {
                setTimeout(() => (scroll(stepNum, scrollStep, vector)), i * 5)
            }
        }
    };

    useEffect(() => {
        // console.log(gl.current);
    }, [])

    const ScrollButton = withStyles({
        root: {
            width: '100%',
            height: '28%',
            textAlign: 'center',
            position: 'absolute',
            // zIndex: '2',
            color: 'white',
        },
    })(IconButton);
    const ScrollButtonTop = withStyles({
        root: {
            top: '0',
        },
        label:{
            verticalAlign: 'top',
            marginBottom: 'auto',
        },
    })(ScrollButton)
    const ScrollButtonBottom = withStyles({
        root: {
            bottom: '0',
        },
        label:{
            verticalAlign: 'bottom',
            marginTop: 'auto',
        },
    })(ScrollButton)


    // お店画像の描画
    const renderImages = (images) =>{
        return(
            <div className='glWrapper'>
                <GridList
                    className={classes.gridList}
                    cols={props.data.Images.length <= 4 ? 1 : 2}
                    spacing={2}
                    ref={gl}
                >
                    {images.map((tile,i) => (
                        <GridListTile key={props.data.Restaurant_id+i}
                            className={classes.gridListTile}>
                            <img src={tile} alt="" />
                        </GridListTile>
                    ))}
                </GridList>
                <ScrollButtonTop onClick={() => {
                    scrollGrid(-1)
                }}
                    onTouchEnd={() => scrollGrid(-1)}>
                    ^
                </ScrollButtonTop>

                <ScrollButtonBottom onClick={() => {
                    scrollGrid(1)
                }}
                    onTouchEnd={() => scrollGrid(1)}>
                    v
                </ScrollButtonBottom>
                {/* <Divider /> */}
            </div>
        )
    }

    // お店情報の描画
    const renderCardContent = (data) =>{
        return (
            <div className={"cardContentWrapper"}>
                <CardContent className={classes.cardContent}>
                    <Typography className={classes.textShopName}>
                        {data.Name}
                    </Typography>
                    <Divider />
                    <Typography className={classes.textSecondary}
                        color="primary">
                        <span className={classes.textStars}>
                            {data.ReviewRating}
                        </span>
                    </Typography>
                    <Typography className={classes.textSecondary}>
                        {data.Category === ""
                            ? "カテゴリなし"
                            : data.Category}
                        {space}
                        {data.Price === ""
                            ? ""
                            : "~" + data.Price + "円"}
                        {space}{data.Distance}
                    </Typography>
                    <Typography className={classes.textSecondary}>
                        {data.BusinessHour}
                    </Typography>
                </CardContent>
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
        <div className="RestaurantInformation" style={props.wrapperStyle}>
            <Card variant="outlined" className={classes.cardRoot}>
                {renderImages(props.data.Images)}
                {renderCardContent(props.data)}
                {renderButtons()}
            </Card>
        </div>
    )
}

export default RestaurantInformation
