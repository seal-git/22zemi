import { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import PersonIcon from '@material-ui/icons/Person';
import GroupIcon from '@material-ui/icons/Group';
import SettingsIcon from '@material-ui/icons/Settings';

const useStyles = makeStyles({
  root: {
  },
});

// ナビゲーション
export default function AppBottomNavigation(props) {
  const classes = useStyles();
  const [value, setValue] = useState(0);

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
      <BottomNavigationAction label="ひとりで" icon={<PersonIcon />} onClick={()=>{ props.setView("Alone") }} />
      <BottomNavigationAction label="設定" icon={<SettingsIcon />} onClick={()=>{ props.setView("Setting") }} />
      <BottomNavigationAction label="みんなで" icon={<GroupIcon />} onClick={()=>{ props.setView("Group") }} />
    </BottomNavigation>
    </div>
  );
}