import './Setting.css'
import { Button, Grid,FormControl,Input, Container,TextField, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/core";
import SearchButtonOne from "./search_button_one.png"
import SearchButtonAll from "./search_button_all.png"
// 設定画面

const getCurrentTime = () => {
  const date = new Date()
  const time = ('00' + date.getHours().toString()).slice(-2) + ':' + ('00'+date.getMinutes().toString()).slice(-2)
  console.log(time)
  return time
}

function Setting(props) {
  const proceedToSelection = (newMode,groupId) => {
    if(newMode!==props.mode){
      props.turnMode(groupId)
    }
    props.setView("Selection")
  }
  const CustomTextField = (props) => {
    return(
      <Input defaultValue={props.defaultValue} inputProps={{ 'aria-label': 'description' }} />
    )
  }
  const TimePicker = () => {
    return (
      <form className='container' noValidate>
        <TextField
          id="time-local"
          type="time"
          defaultValue={getCurrentTime()}
          inputProps={{ min: 0, style: { textAlign: 'left' } }}
          InputLabelProps={{
            shrink: false,
          }}
        />
      </form>
    );
  }
  return (
    <div className="setting">
      <h1>飯T</h1>
      <Grid container spacing={2}>
        <Grid item xs='4' className='label-area'>
          <Typography>エリア</Typography>
        </Grid>
        <Grid item xs='7'>
          <CustomTextField defaultValue="四ツ谷駅"></CustomTextField>
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs='4' className='label-genre'>
          ジャンル
        </Grid>
        <Grid item xs='7'>
          <CustomTextField defaultValue="居酒屋"></CustomTextField>
        </Grid>
      </Grid>
      <Grid container spacing={2}>
        <Grid item xs='4' className='label-time'>
          時間
        </Grid>
        <Grid item xs='7'>
          <TimePicker />
        </Grid>
      </Grid>
      <button className="button-alone" onClick={()=>{proceedToSelection("Alone","")}}>
        <img 
          src={SearchButtonOne}
          className={"button-alone-image"}
          alt={"ButtonAlone"} />
      </button>
      <button className="button-group" onClick={()=>{proceedToSelection("Group","")}}>
        <img 
          src={SearchButtonAll}
          className={"button-group-image"}
          alt={"ButtonGroup"} />
      </button>
    </div>
  );
}
export default Setting;
