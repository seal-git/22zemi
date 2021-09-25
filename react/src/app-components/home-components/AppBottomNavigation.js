import React, { useEffect,useState } from 'react'
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
  },
  Notifier: {
    background: '#0070bb',
    border: '#fff',
    position: 'absolute',
    borderRadius: '50%',
    margin: '-.8rem 0 0 0',
    right: '8%',
    width: '1.5rem',
    height: '1.5rem',
    color: 'white',
    fontSize: '1rem',
    textAlign: 'center',
    lineHeight: '1.3rem',
  }
})

/*
 ナビゲーション
*/
export default function AppBottomNavigation(props) {
  const [keepNumber, setKeepNumber] = useState(0)
  const config = {
    height : props.view==='Setting'?'5%'
            :props.view==='Selection'?'10%'
            :'10%',
  }
  const classes = useStyles(config)
  const moveToSetting = () => {
    props.keepNumberRef.current = 0
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
        {keepNumber>0?
        <div className={classes.Notifier}>
            {keepNumber}
        </div>:null}
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

  useEffect( () => {
      setInterval(
          ()=>{
          const v = props.keepNumberRef.current
          if(v===undefined || v===null){v=0}
          setKeepNumber(v)
        },300)
    // Mount 時にだけ呼び出す
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

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