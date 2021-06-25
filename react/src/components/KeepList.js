import KeepListTile from "./KeepListTile";
import { useEffect, useState } from "react";
import axios from "axios";
import sampleData from "./sampleData.json";

import { makeStyles } from '@material-ui/core/styles';



function KeepList(props) {

    const sample = sampleData;

    console.log(sample)

    return (
        <div>
            <h1>キープリスト</h1>
            {sample.map((data) => (
                <KeepListTile data={data} />
            ))}
        </div>
    );
}

export default KeepList;