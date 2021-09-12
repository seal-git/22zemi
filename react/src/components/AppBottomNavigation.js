import React from 'react'
// パッケージからインポート
import { makeStyles } from '@material-ui/core/styles'

const useStyles = makeStyles({
  AppBottomNavigation: {
    width: '100%',
    height: config => config.height,
    position: 'fixed',
    right: '0',
    left: '0',
    bottom: '0',
  },
  Content: {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-evenly',
  },
  Button: {
    height: '60%',
    width: '25%',
    border: 'none',
    padding: '0',
    color: 'white',
    background: '#ff7474',
    // boxShadow: '5px 5px 4px rgba(0, 0, 0, 0.75)',
    borderRadius: '9px',
    cursor: 'pointer',
  }
})

/*
 ナビゲーション
*/
export default function AppBottomNavigation(props) {
  const config = {
    height : props.view==='Setting'?'0':'60px',
  }
  const classes = useStyles(config)
  const moveToSetting = () => {
    props.setView('Setting')
  }
  const moveToSelection = () => {
    props.setView('Selection')
  }
  const moveToKeepList = () => {
    props.setView('KeepList')
  }

  const renderOnSelection = () => {
    return(
      <div className={classes.Content}>
        <button className={classes.Button} onClick={() => { moveToSetting() }}>
          &lt; 条件の設定
        </button>
        <button className={classes.Button} onClick={() => { moveToKeepList() }}>
          結果をみる &gt;
        </button>
      </div>
    )
  }
  
  const renderOnKeepList = () => {
    return(
      <div className={classes.Content}>
        <button className={classes.Button} onClick={() => { moveToSelection() }}>
          &lt; スワイプに戻る
        </button>
      </div>
    )
  }

  return (
    <div className={classes.AppBottomNavigation} id="AppBottomNavigation">
      {
        props.view==='Selection'? renderOnSelection()
        :props.view==='KeepList'? renderOnKeepList()
        :null
      }
    </div>
  );
}