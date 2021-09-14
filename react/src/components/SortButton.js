import React, { useState, useEffect } from 'react'
// パッケージからインポート
import { makeStyles } from '@material-ui/core/styles'

const useStyles = makeStyles({
    sortButtonActive: {
        // display: 'inline',
        backgroundColor: "#D90060",
        color: "#FFF",
        fontWeight: "700",
        padding: "2px 8px",
        margin: "8px 4px 0",
        borderRadius: "30px",
        fontSize: "11px",
        textAlign: "center",
        cursor: "pointer",
    },
    sortButtonInactive: {
        // display: 'inline',
        backgroundColor: "#C8C8C8",
        color: "#373737",
        fontWeight: "700",
        padding: "2px 8px",
        margin: "8px 4px 0",
        borderRadius: "30px",
        fontSize: "11px",
        textAlign: "center",
        cursor: "pointer",
    }
})
/*
 ナビゲーション
*/
export default function SortButton(props) {
    const classes = useStyles()

    const onSortButtonClicked = () => {
        props.setSortMode(props.sortType)
        // KeepListのselectControl()を実行
        props.onClick(props.sortType)
    }

    return (
        <div
            className={props.sortType == props.sortMode
                ? classes.sortButtonActive
                : classes.sortButtonInactive}
            onClick={() => { onSortButtonClicked() }}
        >
            {props.text}
        </div>
    );
}
