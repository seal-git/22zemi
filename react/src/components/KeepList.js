import KeepListTile from "./KeepListTile";
import { useEffect, useState } from "react";
import axios from "axios";
import sampleData from "./sampleData.json";

import { makeStyles } from '@material-ui/core/styles';
import { Box } from "@material-ui/core";
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';

const useStyles = makeStyles((theme) => ({
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
    },
    select: {
        height: '40px',
        color: 'black',
        background:
            'linear-gradient(116.73deg, #FFCD4E 27.25%, #FFB74A 71.71%)',
        border: '0px',
        borderRadius: '10px'
    }
}));

function KeepList(props) {

    const classes = useStyles();

    const sample = sampleData;

    console.log(sample)

    return (
        <div>
            <Box>
                <FormControl variant="outlined" className={classes.formControl}>
                    <Select
                        native
                        value="osusu"
                        inputProps={{
                            name: 'age',
                            id: 'outlined-age-native-simple',
                        }}
                        className={classes.select}
                        onChange={selectControll}
                        id="select"
                    >
                        <option value={10} >おすすめ順</option>
                        <option value={20}>評価が高い順</option>
                        <option value={30}>距離が近い順</option>
                    </Select>
                </FormControl>
            </Box>
            {sample.map((data) => (
                <KeepListTile data={data} />
            ))}
        </div>
    );
}

function selectControll() {
    console.log("a");

}

export default KeepList;