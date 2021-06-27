import { makeStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import "./AppBottomNavigation.css"
import SearchIcon from './footer_icon_search.png'
import SwipeIcon from './footer_icon_swipe.png'
import ListIcon from './footer_icon_list.png'
import SearchIconSelected from './footer_icon_search_selected.png'
import SwipeIconSelected from './footer_icon_swipe_selected.png'
import ListIconSelected from './footer_icon_list_selected.png'
import FooterBackground from './footer_background.png'
import { Box, Container } from '@material-ui/core';
import Image from 'react'
//App
const useStyles = makeStyles({
  AppBottomNavigation: {
  },
});
// ナビゲーション
export default function AppBottomNavigation(props) {
  const classes = useStyles();
  const moveToSetting = () => {
    props.setView('Setting')
  }
  const moveToSelection = () => {
    props.setView('Selection')
  }
  const moveToKeepList = () => {
    props.setView('KeepList')
  }

  return (
    <div className={classes.AppBottomNavigation}>
      <figure>
        <img
          src={FooterBackground}
          alt="footerBackground"
          className="footer-background"
        />
      </figure>
      
      <button className={"button-search"} onClick={()=>{moveToSetting()}}>
        <img 
          src={
            props.view==="Setting"
            ?SearchIconSelected
            :SearchIcon}
          className={"button-search-icon"}
          alt={"ButtonSearchIcon"} />
      </button>
      <button className={"button-swipe"} onClick={()=>{moveToSelection()}}>
        <img 
          src={
            props.view==="Selection"
            ?SwipeIconSelected
            :SwipeIcon}
          className={"button-swipe-icon"}
          alt={"ButtonSwipeIcon"} />
      </button>
      <button className={"button-list"} onClick={()=>{moveToKeepList()}}>
        <img 
          src={
            props.view==="KeepList"
            ?ListIconSelected
            :ListIcon}
          className={"button-list-icon"}
          alt={"ButtonListIcon"} />
      </button>
    </div>
  );
}