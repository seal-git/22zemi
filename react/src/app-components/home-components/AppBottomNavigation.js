import React from 'react'
// パッケージからインポート
import { makeStyles } from '@material-ui/core/styles'
// 他ファイルからインポート
import { ReactComponent as GoSetting } from './../../img/navigation-go-setting.svg'
import { ReactComponent as GoResult } from './../../img/navigation-go-result.svg'
import Credit from './Credit'

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
    width: '35%',
    height: 'auto',
    padding: '0',
    top: '0',
    bottom: '0',
    margin: 'auto',
    border: 'none',
    background: 'transparent',
    cursor: 'pointer',
  }
})

/*
 ナビゲーション
*/
export default function AppBottomNavigation(props) {
  const config = {
    height : props.view==='Setting'?'5%'
            :props.view==='Setting'?'10%'
            :'10%',
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
        <GoSetting 
          className={classes.Button} 
          onClick={() => { moveToSetting() }}
        />
        <GoResult 
          className={classes.Button} 
          onClick={() => { moveToKeepList() }}
        />
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
      <Credit />
    </div>
  );
}