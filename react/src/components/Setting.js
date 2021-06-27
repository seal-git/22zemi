import { Button, Grid,FormControl,Select, Container } from "@material-ui/core";
import { makeStyles } from "@material-ui/core";

// 設定画面

const useStyles = makeStyles({
  Setting: {
    textAlign: 'center',
  },
});

function Setting(props) {
  const proceedToSelection = (newMode,groupId) => {
    if(newMode!==props.mode){
      props.turnMode(groupId)
    }
    props.setView("Selection")
  }
  const classes = useStyles()
  return (
    <div className={classes.Setting}>
      <h1>飯T</h1>
      <Grid container>
        <Grid item xs='6'>
          エリア
        </Grid>
        <Grid item xs='6'>
          <FormControl>
            <Select id="select">
              <option value="hoge">Hoge</option>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      <Grid container>
        <Grid item xs='6'>
          ジャンル
        </Grid>
        <Grid item xs='6'>
          <FormControl>
            <Select id="select">
              <option value="hoge">Hoge</option>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      <Grid container>
        <Grid item xs='6'>
          人数
        </Grid>
        <Grid item xs='6'>
          <FormControl>
            <Select id="select">
              <option value="hoge">Hoge</option>
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      <Container>
        <Button variant="contained" color="primary" onClick={()=>{proceedToSelection("Alone",'--')}}>ひとりで決める</Button>
      </Container>
      <Container>
        <Button variant="contained" color="secondary" onClick={()=>{proceedToSelection("Group",'--')}}>みんなで決める</Button>
      </Container>
    </div>
  );
}
export default Setting;
