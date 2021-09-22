import React from 'react'
import { Grid } from "@material-ui/core"
import { makeStyles,withStyles } from '@material-ui/core'

// 他ファイルからインポート
import CircleIcon from './../../../icon/CircleIcon.js'
import CrossIcon from './../../../icon/CrossIcon.js'

/* 
ボタンをGridでまとめたもの
*/

const useStyles = makeStyles({
  Buttons:{
      position: 'absolute',
      bottom: '5%',
      width: '100%',
      textAlign: 'center',
  },
})

const StyledCircleIcon = withStyles({
    root: {
      width: '30%',
      height: 'auto',
      position: 'relative',
      cursor: 'pointer',
    },
})(CircleIcon);

const StyledCrossIcon = withStyles({
    root: {
      width: '30%',
      height: 'auto',
      position: 'relative',
      cursor: 'pointer',
    },
})(CrossIcon);

function Buttons(props) {
  const classes = useStyles()

  const RejectButton = () => {
    return <StyledCrossIcon onClick={()=>{props.reject()}}/>
  }
  const KeepButton = () => {
    return <StyledCircleIcon onClick={()=>{props.keep()}}/>
  }
  return (
      <Grid container spacing={0} className={classes.Buttons}>
        <Grid item xs={6}><RejectButton /></Grid>
        <Grid item xs={6}><KeepButton /></Grid>
      </Grid>
  );
}
export default Buttons;