import React from 'react'
import { Grid } from "@material-ui/core"
import { makeStyles } from '@material-ui/core'

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
  RejectButton :{
    width: '60px',
    height: '60px',
    backgroundColor: '#ff7474',
    borderRadius: '50%',
    position: 'relative',
    cursor: 'pointer',
    '&:before':{
      content: '""',
      backgroundColor: 'white',
      width: '50px',
      height: '8px',
      top: '6px',
      left: '10px',
      transform: 'rotate(45deg)',
      transformOrigin: '0% 50%',
      position: 'absolute',
    },
    '&:after':{
      content: '""',
      backgroundColor: 'white',
      width: '50px',
      height: '8px',
      top: '6px',
      right: '10px',
      transform: 'rotate(-45deg)',
      transformOrigin: '100% 50%',
      position: 'absolute',
    }
  },
  KeepButton :{
    width: '60px',
    height: '60px',
    backgroundColor: 'white',
    border: 'solid #34a2e0 8px',
    borderRadius: '50%',
    position: 'relative',
    boxSizing: 'border-box',
    cursor: 'pointer',
    '&:after':{
      content: '""',
      width: '30px',
      height: '30px',
      top: '7px',
      left: '7px',
      position: 'absolute',
      backgroundColor: '#34a2e0',
      borderRadius: '50%',
      boxSizing: 'border-box',
    }
  },
})

function Buttons(props) {
  const classes = useStyles()

  const RejectButton = () => {
    return <button  onClick={() => { props.reject() }} className={classes.RejectButton}></button>
  }
  const KeepButton = () => {
    return <button  onClick={() => { props.keep() }} className={classes.KeepButton}></button>
  }
  return (
    <div className={classes.Buttons}>
      <Grid container spacing={0}>
        <Grid item xs={6}><RejectButton /></Grid>
        <Grid item xs={6}><KeepButton /></Grid>
      </Grid>
    </div>
  );
}
export default Buttons;