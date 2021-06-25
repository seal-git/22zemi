import { IconButton,Grid } from "@material-ui/core";
import ClearIcon from '@material-ui/icons/Clear';
import DirectionsWalkIcon from '@material-ui/icons/DirectionsWalk';
import FavoriteIcon from '@material-ui/icons/Favorite';
import ScheduleIcon from '@material-ui/icons/Schedule';

// ボタンをGridでまとめたもの
function Buttons(props) {
  return(
    <div className="Buttons">
      <Grid container spacing={1}>
        <Grid item xs={6}><RejectButton reject={props.reject}/></Grid>
        <Grid item xs={6}><KeepButton keep={props.keep}/></Grid>
      </Grid>
    </div>
  );
}

function RejectButton(props){
    return <IconButton color="primary" component="span" onClick={ ()=>{props.reject()}}><ClearIcon /></IconButton>
}
function KeepButton(props){
    return <IconButton color="primary" component="span" onClick={ ()=>{props.keep()}}><FavoriteIcon /></IconButton>
}

export default Buttons;