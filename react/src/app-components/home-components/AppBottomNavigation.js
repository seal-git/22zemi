import React from 'react'
// パッケージからインポート
import { makeStyles } from '@material-ui/core/styles'
// 他ファイルからインポート
import { ReactComponent as GoSetting } from './../../img/navigation-go-setting.svg'
import { ReactComponent as GoResult } from './../../img/navigation-go-result.svg'
import { ReactComponent as ReturnSwipe } from './../../img/navigation-return-swipe.svg'
import Credit from './Credit'

const useStyles = makeStyles({
  AppBottomNavigation: {
    width: '100%',
    height: config => config.height,
    position: 'fixed',
    right: '0',
    left: '0',
    bottom: '0',
    backgroundColor: 'white',
  },
  Content: {
    width: '100%',
    height: '30%',
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
            :props.view==='Selection'?'10%'
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
          onClick={moveToSetting}
        />
        <GoResult 
          className={classes.Button} 
          onClick={moveToKeepList}
        />
      </div>
    )
  }
  
  const renderOnKeepList = () => {
    return(
      <div className={classes.Content}>
        <ReturnSwipe 
            className={classes.Button} 
            onClick={moveToSelection} 
        />
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