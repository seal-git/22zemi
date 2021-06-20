import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import MenuBookIcon from '@material-ui/icons/MenuBook';
import TouchAppIcon from '@material-ui/icons/TouchApp';

const useStyles = makeStyles({
  root: {
  },
});

// ナビゲーションを使ってみる
export default function AppBottomNavigation(props) {
  const classes = useStyles();
  const [value, setValue] = React.useState(0);

  return (
    <div className='AppBottomNavigation'>
    <BottomNavigation
      value={value}
      onChange={(event, newValue) => {
        setValue(newValue);
      }}
      showLabels
      className={classes.root}
    >
      <BottomNavigationAction label="Swipe" icon={<TouchAppIcon />} onClick={()=>{ props.setView("Swipe") }} />
      <BottomNavigationAction label="Keep List" icon={<MenuBookIcon />} onClick={()=>{ props.setView("KeepList")}}/>
    </BottomNavigation>
    </div>
  );
}