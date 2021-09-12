import React from 'react'
import "./Keeplist.css"
// パッケージからインポート
import { useEffect, useState, useRef } from "react"
import axios from "axios"
import { makeStyles } from '@material-ui/core/styles'
import { Box } from "@material-ui/core"
import FormControl from '@material-ui/core/FormControl'
import Select from '@material-ui/core/Select'
import Typography from '@material-ui/core/Typography'
// 他のファイルからインポート
import Credit from "./Credit"
import KeepListTile from "./KeepListTile"
import noImageIcon from "..//img/no_image.png"

const useStyles = makeStyles((theme) => ({
    aloneStyle: {
        minHeight: '100%',
        backgroundImage: 'linear-gradient(180.02deg, #FFEEAA 0.02%, #FDFFEB 80.2%)',
        backgroundSize: 'cover',
    },
    groupStyle: {
        minHeight: '100%',
        backgroundImage: 'linear-gradient(180.02deg, #FFDDAA 0.02%, #FFFBFB 80.2%)',
        backgroundSize: 'cover',
    },
    topWrapper: {
        display: 'flex',
    },
    participantNum: {
        lineHeight: '25px',
        textAlign: 'center',
        margin: '8px 0px 10px auto',
        padding: '3px 15px 0 20px',
        backgroundColor: '#FFECC8',
        borderRadius: '24px 0 0 24px',
        borderLeft: 'solid 1px #A03A00',
        borderTop: 'solid 1px #A03A00',
        borderBottom: 'solid 1px #A03A00',
        fontSize: '0.8rem',
    },
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
    },
    select: {
        color: 'black',
        background:
            'linear-gradient(116.73deg, #FFCD4E 27.25%, #FFB74A 71.71%)',
        border: '0px',
        borderRadius: '10px',
        fontSize: '0.8rem',
    },
    spacerBottom: {
        height: '60px'
    }
}));

const initDataList = [{
    "Name": "Loading...",
    "Images": [noImageIcon, noImageIcon],
    "Distance": "",
    "Price": "",
    "Category": "",
    "ReviewRating": "",
    "VotesLike": 0,
    "VotesAll": 0,
    "distance_float": 0.,
    "RecommendScore": 0,
}, {
    "Name": "Loading...",
    "Images": [noImageIcon, noImageIcon],
    "Distance": "",
    "Price": "",
    "Category": "",
    "ReviewRating": "",
    "VotesLike": 0,
    "VotesAll": 0,
    "distance_float": 0.,
    "RecommendScore": 0,
}]


/*
キープしたお店の一覧を表示するコンポーネント
 */
function KeepList(props) {

    const classes = useStyles();
    const selectRef = useRef(null);
    const [dataList, setDataList] = useState(initDataList)

    // ソート方法を決める値
    const sortByRecommendScore = 10
    const sortByDistance = 20
    const sortByFeeAscend = 30
    const sortByFeeDescend = 40

    // APIからキープリストのデータを得る
    const getList = () => {
        const params = { "user_id": props.userId }
        if (props.mode === "Group") {
            params["group_id"] = props.groupId
        }
        console.log(params)
        axios.post('/api/list', {
            params: params
        })
            .then(function (response) {
                console.log(response)
                let dataList = response['data']
                if(dataList === 0){
                    console.log("no data")
                    dataList = []
                }else {
                    dataList.sort(function (a, b) {
                        // 降順ソート
                        if (+a.RecommendScore > +b.RecommendScore) return -1
                        if (+a.RecommendScore < +b.RecommendScore) return 1
                        return 0
                    });
                    dataList.sort(function (a, b) {
                        // 降順ソート
                        if (+a.VotesLike > +b.VotesLike) return -1
                        if (+a.VotesLike < +b.VotesLike) return 1
                        return 0
                    });
                }
                console.log("keeplist length:"+dataList.length)
                setDataList(dataList)
            })
            .catch((error) => {
                console.log(error);
            });
    }

    useEffect(() => {
        getList()
        // Mount 時にだけ呼び出す
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    // モードが切り替わるとスタイルが変わる
    // Appが指定している高さをぶち抜いてリストが表示されるので
    // 全体に背景色を適用させるために、あらためて背景色を設定する
    const [className, setClassName] = useState(classes.AppAlone);
    useEffect(() => {
        if (props.mode === "Alone") {
            setClassName(classes.aloneStyle)
        } else if (props.mode === "Group") {
            setClassName(classes.groupStyle)
        }
        // classes は引数から除外
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [props.mode])

    const selectControl = (event) => {
        // ソート用にリストを複製
        let newDataList = [...dataList]
        if (newDataList.length>0) {

            // ソートの条件を取得
            // 注：文字列型として扱われるのを回避するため + で数値に変換
            let sortValue = +event.target.value
            // 条件に合わせてソートを実行

            if (sortValue === sortByRecommendScore) {
                console.log('sort by recommend score')
                newDataList.sort(function (a, b) {
                    // おすすめ度で降順ソート
                    if (+a.RecommendScore > +b.RecommendScore) return -1
                    if (+a.RecommendScore < +b.RecommendScore) return 1
                    return 0
                })
                newDataList.sort(function (a, b) {
                    // 投票数で降順ソート
                    if (+a.VotesAll > +b.VotesAll) return -1
                    if (+a.VotesAll < +b.VotesAll) return 1
                    return 0
                })
            } else if (sortValue === sortByDistance) {
                console.log('sort by distance')
                newDataList.sort(function (a, b) {
                    // 距離で昇順ソート
                    if (+a.distance_float > +b.distance_float) return 1
                    if (+a.distance_float < +b.distance_float) return -1
                    return 0
                })
            } else if (sortValue === sortByFeeAscend) {
                console.log('sort by fee; ascending')
                newDataList.sort(function (a, b) {
                    // 価格帯で昇順ソート
                    if (+a.Price > +b.Price) return 1
                    if (+a.Price < +b.Price) return -1
                    return 0
                })
            } else if (sortValue === sortByFeeDescend) {
                console.log('sort by fee; descending')
                newDataList.sort(function (a, b) {
                    // 価格帯で降順ソート
                    if (+a.Price > +b.Price) return -1
                    if (+a.Price < +b.Price) return 1
                    return 0
                })
            }
        }
        // ソート結果を反映
        console.log(newDataList)
        setDataList(newDataList)

        // フォーカスを外さないと見た目が残念になる
        var obj = document.activeElement
        if (obj) {
            obj.blur()
        }
    }

    const KeepListTiles = () => {
        return (
            dataList.map((data) => (
                <KeepListTile data={data} mode={props.mode} />
            ))
        )
    }

    const getNumberOfParticipants = () => {
        if(dataList.length > 0) {
            return dataList[0].NumberOfParticipants
        }else{
            return 0
        }
    }

    return (
        <div className="Keeplist-wrapper">
            <div className="Keeplist">
                <div className={className}>
                    <Box className={classes.topWrapper}>
                        <FormControl variant="outlined"
                            className={classes.formControl}>
                            <Select
                                native
                                inputProps={{
                                    name: 'age',
                                    id: 'outlined-age-native-simple',
                                }}
                                className={classes.select}
                                onChange={(event) => {
                                    selectControl(event)
                                }}
                                id="selectRef"
                                ref={selectRef}
                            >
                                <option value={sortByRecommendScore}>おすすめ順</option>
                                <option value={sortByFeeAscend}>予算が低い順</option>
                                <option value={sortByDistance}>距離が近い順</option>
                                <option value={sortByFeeDescend}>予算が高い順</option>
                            </Select>
                        </FormControl>
                        <Typography className={classes.participantNum}
                            style={props.mode === "Alone" ? { display: "none", } : { display: "block", }}>
                            投票人数 {getNumberOfParticipants()}人
                        </Typography>
                    </Box>
                    <Box>
                        {dataList.length > 0 ?
                            <KeepListTiles /> :
                            <Typography>
                                キープされたお店はありません
                            </Typography>}
                    </Box>
                    {/* <Box style={{ height: '48px' }}></Box> */}
                </div>
            </div>
            <Credit />
        </div>
    )
}

export default KeepList
