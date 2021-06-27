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
    topWrapper: {
        display: 'flex'
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
    }
}));

function KeepList(props) {

    const classes = useStyles();
    const sample = sampleData;
    const selectRef = useRef(null);

    const selectControll = (event) => {

        console.log(event.target.value)
        // フォーカスを外さないと見た目が残念になる
        var obj = document.activeElement;
        if (obj) {
            obj.blur();
        }
    }

    console.log(sample)

    return (
        <div>
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
                <Typography className={classes.participantNum}>
                    投票人数 未実装人
                </Typography>
            </Box>
            {sample.map((data) => (
                <KeepListTile data={data} />
            ))}
        </div>
    );
}


export default KeepList;