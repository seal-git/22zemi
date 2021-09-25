import React from 'react'
// パッケージからインポート
import { useState, useEffect } from 'react'
import Box from '@material-ui/core/Box'

function Bar(props){
    const background=props.isSelected===true?'rgba(255,255,255,1)':'rgba(0,0,0,.4)'
    return (
        <Box
            height='100%'
            width='100%'
            boxShadow='0px 4px 4px rgba(0, 0, 0, 0.75)'
            border='2px solid gray'
            borderRadius='10%'
            margin='1%'
            cursor='pointer'
            css={{background:background}}
            onClick={props.onClick}
        />
    )
}

function Bars(props){
    return(
        <Box 
            width='80%'
            height='1%'
            top='5%'
            left='10%'
            display='flex'
            position='absolute'
        >
            {props.Images.map( (image,i) =>{
                return <Bar isSelected={i===props.index} onClick={()=>{ props.setIndex(i)}} />
            })} 
        </Box>
    )
}

function RestaurantImage(props){
    return(
        <img 
            id={props.restaurant_id+'-image'+props.i}
            alt={'restaurant-image'+props.i}
            src={props.image} 
            style={
                {
                    opacity: props.isSelected?1:0, 
                    transition:'0.5s',
                    width: props.restaurant_id==='tutorial'?'100%':'auto',
                    height: props.restaurant_id==='tutorial'?'auto':'100%',
                    objectFit: 'cover',
                    backgroundColor: 'transparent',
                    webkitUserSelect: 'none',
                    mozUserSelect: 'none',
                    MsUserSelect: 'none',
                    userSelect: 'none',
                    pointerEvents: 'none',
                    willChange: 'opacity',
                    position: 'absolute',
                }}
        />
    )
}

// バー付きの画像を表示する
function ImageArea(props){
    const [index, setIndex] = useState(0)

    useEffect(() => {
        console.log('imageArea:',props)
        const currentIndex = index
        const t = setInterval(
            () => {
                if(currentIndex!==undefined && currentIndex===index){
                    setIndex(state => (state + 1) % props.Images.length)
                }
            }
        , 2500)
        return ()=>{clearInterval(t)}
    },[index])

    return(
        <Box>
            <Box 
                position='absolute'
                width='100%'
                height='100%'
                backgroundColor='transparent'
            >
                {props.Images.map( (image,i)=>{
                    return <RestaurantImage image={image} i={i} restaurant_id={props.restaurant_id} isSelected={index===i}/>
                })}
            </Box>
            {
                props.restaurant_id!=='tutorial'
                ?<Box
                    style={ {
                        width:'100%',
                        height:'100%',
                        position:'absolute',
                        background:`linear-gradient( rgba(0, 0, 0, 0), rgba(0, 0, 0, 0) 70%,rgba(0, 0, 0, 1) 85%, rgba(0, 0, 0, 1))`,
                    } }
                > </Box>
                :null
            }
            {
                props.restaurant_id!=='tutorial'
                ?  <Bars Images={props.Images} index={index} setIndex={setIndex}/>
                :  null
            }
        </Box>
    )
}
export default ImageArea