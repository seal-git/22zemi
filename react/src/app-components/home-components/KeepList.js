import React from 'react'
import "./../../css/Keeplist.css"
// パッケージからインポート
import { useEffect, useState, useRef } from "react"
import axios from "axios"
import { makeStyles } from '@material-ui/core/styles'
import { Box, Grid } from "@material-ui/core"
import Typography from '@material-ui/core/Typography'
// 他のファイルからインポート
import Credit from "./Credit"
import KeepListTile from "./keeplist-components/KeepListTile"
import sampleData from "./../../samples/sampleData2.json"
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import SortButton from './keeplist-components/SortButton'
import KeepListModal from './keeplist-components/KeepListModal'
import { CSSTransition, Transition } from 'react-transition-group';
import CommentModal from './selection-components/restaurant-information-components/CommentModal';
import RestaurantInformation from './selection-components/RestaurantInformation';


const useStyles = makeStyles((theme) => ({

    aloneStyle: {
        height: '100%',
        backgroundColor: 'white',
        // backgroundImage: 'linear-gradient(180.02deg, #FFEEAA 0.02%, #FDFFEB 80.2%)',
        // backgroundSize: 'cover',
    },
    groupStyle: {
        height: '100%',
        backgroundColor: 'white',
        // backgroundImage: 'linear-gradient(180.02deg, #FFDDAA 0.02%, #FFFBFB 80.2%)',
        // backgroundSize: 'cover',
    },
    Keeplist_wrapper: {
        height: "100%",
    },
    KeepList: {
        flex: 1,
        height: '100%',
    },
    topWrapper: {
        width: '100%',
        height: '14%',
    },
    pageTitle: {
        display: 'flex',
        alignItems: 'center',
        height: '50%',
        fontSize: '1.2rem',
        fontWeight: 700,
        backgroundColor: '#D90060',
        color: 'white',
        paddingLeft: '8px'
    },
    sortButtonWrapper: {
        // width: '100%',
        padding: '0 8px',
        display: 'flex',
        height: '50%',
        overflowX: "scroll",
        '&::-webkit-scrollbar': {
            display: 'none'
        }
    },
    modalWrapper: {
        position: 'absolute',
        height: '100%',
        width: '100%',
        justifyContent: 'space-around',
        zIndex: 5,
    },
    tileWrapper: {
        padding: '0px 0 80px 0',
        height: '70%',
        overflowY: "scroll",
        '&::-webkit-scrollbar': {
            display: 'none'
        }
    }
}));

const initDataList = sampleData

// const initDataList = sampleData


/*
キープしたお店の一覧を表示するコンポーネント
 */
function KeepList(props) {

    const classes = useStyles();
    const selectRef = useRef(null);
    const [dataList, setDataList] = useState([])
    const [sortMode, setSortMode] = useState("sortByFavos")

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
                // let dataList = initDataList
                if (dataList === 0) {
                    console.log("no data")
                    dataList = []
                } else {
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
                // console.log("keeplist length:" + dataList.length)
                setDataList(dataList)
            })
            .catch((error) => {
                console.log(error);
            });
    }

    useEffect(() => {
        getList()
        props.setTutorialIsOn(false)
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
        if (newDataList.length > 0) {
            console.log(event)

            if (event == 'sortByFavos') {
                console.log('みんなの人気順')
                newDataList.sort(function (a, b) {
                    // みんなの人気順でソート
                    if (+a.VotesLike > +b.VotesLike) return -1
                    if (+a.VotesLike < +b.VotesLike) return 1
                    return 0
                })
                newDataList.sort(function (a, b) {
                    // 投票数で降順ソート
                    if (+a.VotesAll > +b.VotesAll) return -1
                    if (+a.VotesAll < +b.VotesAll) return 1
                    return 0
                })
            } else if (event == 'sortByHighRated') {
                console.log('評価の高い順')
                newDataList.sort(function (a, b) {
                    // 評価の高い順
                    if (a.ReviewRating != null) {
                        var rateA = +a.ReviewRating.slice(8);
                    } else {
                        var rateA = 0;
                    }
                    if (b.ReviewRating != null) {
                        var rateB = +b.ReviewRating.slice(8);
                    } else {
                        var rateB = 0;
                    }

                    if (rateA > rateB) return -1
                    if (rateA < rateB) return 1
                    return 0
                })
            } else if (event === 'sortByLowPrice') {
                console.log('価格の安い順')
                newDataList.sort(function (a, b) {
                    // 価格の安い順
                    if (+a.Price > +b.Price) return 1
                    if (+a.Price < +b.Price) return -1
                    return 0
                })
            } else if (event == 'sortByRecommended') {
                console.log('おすすめ順')
                newDataList.sort(function (a, b) {
                    // おすすめ順
                    if (+a.RecommendScore > +b.RecommendScore) return -1
                    if (+a.RecommendScore < +b.RecommendScore) return 1
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
                <KeepListTile data={data} mode={props.mode} onClick={openModal} />
            ))
        )
    }

    const getNumberOfParticipants = () => {
        if (dataList.length > 0) {
            return dataList[0].NumberOfParticipants
        } else {
            return 0
        }
    }

    const sortItems = [
        { text: 'みんなの人気順', sortType: 'sortByFavos' },
        { text: '評価の高い順', sortType: 'sortByHighRated' },
        { text: '値段の安い順', sortType: 'sortByLowPrice' },
        { text: 'おすすめ順', sortType: 'sortByRecommended' }
    ];

    const [modalState, setModalState] = useState(false);
    const [modalData, setModalData] = useState(['none']);

    // KeepListTileに渡す関数、モーダルを開状態にしてデータを渡す
    const openModal = (data) => {
        console.log('open modal!')
        setModalState(true);
        setModalData(data);
    }

    // KeepListModalに渡す関数、モーダルを閉状態にする
    const closeModal = () => {
        setModalState(false);
        // setModalData(['none']);
    }


    return (
        <div className={classes.Keeplist_wrapper}>
            <CommentModal
                open={modalState}
                handleClose={closeModal}
                data={modalData}
                showPicture={true}
            />
            {/* <CSSTransition in={modalState} classNames="modal" timeout={500} unmountOnExit>
                <div className={classes.modalWrapper}>
                    <KeepListModal
                        data={modalData}
                        modalState={modalState}
                        onClick={closeModal} />
                </div>
            </CSSTransition> */}
            <div className={classes.KeepList}>
                <div className={classes.topWrapper}>
                    <Typography className={classes.pageTitle}>
                        みんなの投票結果
                    </Typography>
                    <div className={classes.sortButtonWrapper}>
                        {sortItems.map((item) => (
                            <SortButton
                                text={item.text}
                                sortType={item.sortType}
                                sortMode={sortMode}
                                setSortMode={setSortMode}
                                onClick={selectControl} />
                        ))}
                    </div>
                </div>
                <div className={classes.tileWrapper}>
                    {dataList.length > 0 ?
                        <KeepListTiles /> :
                        <Typography>
                            キープされたお店はありません
                        </Typography>}
                    {/* 画面外にいかないために箱を置いとく */}
                    <div style={{ height: '200px' }}></div>
                </div>
            </div>
            <Credit />
        </div >
    )
}

export default KeepList
