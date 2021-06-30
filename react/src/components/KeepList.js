import React from 'react';
import KeepListTile from "./KeepListTile";
import { useEffect, useState, useRef } from "react";
import axios from "axios";
import sampleData from "./sampleData.json";

import { makeStyles } from '@material-ui/core/styles';
import { Box } from "@material-ui/core";
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
    aloneStyle: {
        height: '100%',
        backgroundImage: 'linear-gradient(180.02deg, #FFEEAA 0.02%, #FDFFEB 80.2%)',
        backgroundSize: 'cover'
    },
    groupStyle: {
        height: '100%',
        backgroundImage: 'linear-gradient(180.02deg, #FFDDAA 0.02%, #FFFBFB 80.2%)',
        backgroundSize: 'cover'
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
        height: '30px',
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
    "Name": "Waiting...", "Images": [""], "Distance": "-m", "Price": "-円",
    "Category": "-", "ReviewRating": "-", "VotesLike": 0, "VotesAll": 0,
}]

function KeepList(props) {

    const classes = useStyles();
    const sample = sampleData;
    const selectRef = useRef(null);
    const [dataList, setDataList] = useState(initDataList)

    // APIからキープリストのデータを得る
    const getList = () => {
        const params = { "user_id": props.userId }
        if (props.mode === "Group") {
            params["group_id"] = props.groupId
        }
        console.log(params);
        axios.post('/api/list', {
            params: params
        })
            .then(function (response) {
                console.log(response)
                let dataList = response['data']
                console.log(dataList[0])
                setDataList(dataList)
            })
            .catch((error) => {
                console.log(error);
            });
    }

    useEffect(() => {
        getList()
    }, []);


    // モードが切り替わるとスタイルが変わる
    // Appが指定している高さをぶち抜いてリストが表示されるので
    // 全体に背景色を適用させるために、あらためて背景色を設定する
    const [className, setClassName] = useState(classes.AppAlone);
    const mode = props.mode;
    useEffect(() => {
        if (mode === "Alone") {
            setClassName(classes.aloneStyle)
        } else if (mode === "Group") {
            setClassName(classes.groupStyle)
        }
        console.log("App:useEffect[mode]")
    }, [mode])

    const selectControll = (event) => {

        console.log(event.target.value)
        // フォーカスを外さないと見た目が残念になる
        var obj = document.activeElement;
        if (obj) {
            obj.blur();
        }
    }

    return (
        <div className={className}>
            <Box className={classes.topWrapper}>
                <FormControl variant="outlined" className={classes.formControl}>
                    <Select
                        native
                        inputProps={{
                            name: 'age',
                            id: 'outlined-age-native-simple',
                        }}
                        className={classes.select}
                        onChange={selectControll}
                        id="selectRef"
                        ref={selectRef}
                    >
                        <option value={10} >未おすすめ順</option>
                        <option value={20}>評価が高い順</option>
                        <option value={30}>距離が近い順</option>
                    </Select>
                </FormControl>
                <Typography className={classes.participantNum}
                    style={props.mode == "Alone" ? { display: "none", } : { display: "block", }}>
                    投票人数 未実装人
                </Typography>
            </Box>
            <Box>
                {dataList.map((data) => (
                    <KeepListTile data={data} mode={mode} />
                ))}
            </Box>
            {/* <Box style={{ height: '48px' }}></Box> */}
        </div >
    );
}


export default KeepList;