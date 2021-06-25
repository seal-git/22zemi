import { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';

const useStyles = makeStyles({
  root: {
  },
});

// ナビゲーション
export default function AppBottomNavigation(props) {
  const classes = useStyles();
  const [value, setValue] = useState(1);

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
      <BottomNavigationAction label="検索条件" onClick={()=>{ props.setView("Setting") }} />
      <BottomNavigationAction label="選択"  onClick={()=>{ props.setView("Selection") }} />
      <BottomNavigationAction label="決定"  onClick={()=>{ props.setView("KeepList") }} />
    </BottomNavigation>
    </div>
  );
}