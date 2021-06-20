import { Button } from "@material-ui/core"
import { useHistory } from "react-router-dom"
import { Grid } from "@material-ui/core"

// 最初の画面
function Entrance() {
  const history = useHistory()
  const handleLink = path => history.push(path)
  return (
    <div className="Entrance">
      <h1>App Name</h1>
      <Grid container spacing={3}>
          <Grid item xs={12}>
            <Button variant="contained" color="primary" onClick={ ()=>{ handleLink("/alone") } }>ひとりで決める</Button>
          </Grid>
          <Grid item xs={12}>
            <Button variant="contained" color="secondary" onClick={ ()=>{ handleLink("/group") } }>みんなで決める</Button>
          </Grid>
          <Grid item xs={12}>
            <Button variant="contained" color="default" onClick={ ()=>{ handleLink("/api-test") } }>test</Button>
          </Grid>
      </Grid>
    </div>
  );
}

export default Entrance;
