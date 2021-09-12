import React, {useState,useEffect} from 'react'
import "./AppBottomNavigation.css"
// パッケージからインポート
import { makeStyles } from '@material-ui/core/styles'
import { withStyles } from '@material-ui/core/styles'
import Badge from '@material-ui/core/Badge'
// 他のファイルからインポート
import SearchIcon from '..//img/footer_icon_search.png'
import SwipeIcon from '..//img/footer_icon_swipe.png'
import ListIcon from '..//img/footer_icon_list.png'
import SearchIconSelected from '..//img/footer_icon_search_selected.png'
import SwipeIconSelected from '..//img/footer_icon_swipe_selected.png'
import ListIconSelected from '..//img/footer_icon_list_selected.png'
import FooterBackground from '..//img/footer_background.png'
import { numGlobal } from './global'

const useStyles = makeStyles({
  AppBottomNavigation: {
    height: '60px',
    position: 'fixed',
    right: '0',
    left: '0',
    bottom: '0',
  },
})
const StyledBadge = withStyles((theme) => ({
  badge: {
    right: -2,
    top: 4,
    // border: `2px solid ${theme.palette.background.paper}`,
    // padding: '0 4px',
  },
}))(Badge)

/*
 ナビゲーション
*/
export default function AppBottomNavigation(props) {
  const classes = useStyles()
  const [numOfCardInKeepList, setNumOfCardInKeepList] = useState(0)
  const moveToSetting = () => {
    props.setView('Setting')
  }
  const moveToSelection = () => {
    props.setView('Selection')
  }
  const moveToKeepList = () => {
    props.setView('KeepList')
  }

  useEffect( ()=>{
    console.log("called")
    setInterval( ()=>{
      setNumOfCardInKeepList(numGlobal)
    } ,500)
  },[])

  return (
    <div className={classes.AppBottomNavigation} id="AppBottomNavigation">
      <figure>
        <img
          src={FooterBackground}
          alt="footerBackground"
          className="footer-background"
        />
      </figure>

      <button className={"button-search"} onClick={() => { moveToSetting() }}>
        <img
          src={
            props.view === "Setting"
              ? SearchIconSelected
              : SearchIcon}
          className={"button-search-icon"}
          alt={"ButtonSearchIcon"} />
      </button>
      <button className={"button-swipe"} onClick={() => { moveToSelection() }}>
        <img
          src={
            props.view === "Selection"
              ? SwipeIconSelected
              : SwipeIcon}
          className={"button-swipe-icon"}
          alt={"ButtonSwipeIcon"} />
      </button>

      <button className={"button-list"} onClick={() => { moveToKeepList() }}>

        <StyledBadge badgeContent={numOfCardInKeepList} color="secondary">
          <img
            src={
              props.view === "KeepList"
                ? ListIconSelected
                : ListIcon}
            className={"button-list-icon"}
            alt={"ButtonListIcon"} />
        </StyledBadge>
      </button>
    </div>
  );
}