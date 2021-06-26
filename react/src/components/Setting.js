import { Button, Grid,FormControl,Select, Container } from "@material-ui/core";

// 設定画面
function Setting(props) {
  return (
    <div className="Setting">
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
        <Button>ひとりで決める</Button>
      </Container>
      <Container>
        <Button>みんなで決める</Button>
      </Container>
    </div>
  );
}
export default Setting;
