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
        <Grid item xs={3}><RejectButton reject={props.reject}/></Grid>
        <Grid item xs={3}><DirectButton direct={props.direct}/></Grid>
        <Grid item xs={3}><ReserveButton reserve={props.reserve}/></Grid>
        <Grid item xs={3}><KeepButton keep={props.keep}/></Grid>
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
function ReserveButton(props){
    return <IconButton color="primary" component="span" onClick={ ()=>{props.reserve()}}><ScheduleIcon /></IconButton>
}
function DirectButton(props){
    return <IconButton color="primary" component="span" onClick={ ()=>{props.direct()}}><DirectionsWalkIcon /></IconButton>
}

export default Buttons;