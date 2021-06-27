import { useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import "./AppBottomNavigation.css"

//App
const useStyles = makeStyles({
  AppBottomNavigation: {
    // width: '100%',
    // position: 'fixed',
    // bottom: 0,
  },
});

// ナビゲーション
export default function AppBottomNavigation(props) {
  const classes = useStyles();
  const [value, setValue] = useState(1);

  return (
    <div className={classes.AppBottomNavigation}>
      {/* <Grid 
      container 
      >
        <Grid item xs={4}>
            <button onClick={() => { props.setView("Setting") }} className={classes.Button} >
              <div className={classes.img}>
                <img src={SearchIcon}
                  className={"search-icon"}
                  alt={"SearchIcon"} />
              </div>
            </button>
        </Grid>
        <Grid item xs={4}>
          <button onClick={()=>{props.setView("Selection")}} className={classes.Button}>
            <img src={SwipeIcon}
              className={"swipe-icon"}
              alt={"SwipeIcon"} />
          </button>
        </Grid>
        <Grid item xs={4}>
          <button onClick={()=>{props.setView("KeepList")}} className={classes.Button}>
            <img src={ListIcon}
              className={"list-icon"}
              alt={"ListIcon"} />
          </button>
        </Grid>
      </Grid> */}
      <BottomNavigation
        value={value}
        onChange={(event, newValue) => {
          setValue(newValue);
        }}
        showLabels
        // className={classes.root}
      >
        <BottomNavigationAction label="検索条件" onClick={() => { props.setView("Setting") }} />
        <BottomNavigationAction label="選択" onClick={() => { props.setView("Selection") }} />
        <BottomNavigationAction label="決定" onClick={() => { props.setView("KeepList") }} />
      </BottomNavigation>
    </div>
  );
}