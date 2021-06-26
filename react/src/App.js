import './App.css';
import ApiTest from './components/ApiTest'
import Home from './components/Home'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { makeStyles } from '@material-ui/core/styles';
import { createMuiTheme } from '@material-ui/core/styles';
import yello from '@material-ui/core/colors/yellow';

import { ThemeProvider } from "@material-ui/styles";

const theme = createMuiTheme({
  palette: {
    primary: {
      main: yello[700],
    },
    secondary: {
      main: '#f44336',
    },
  },
});

const useStyles = makeStyles((theme) => ({
  App: {
    backgroundImage: 'linear-gradient(180.02deg, #FFEEAA 0.02%, #FDFFEB 80.2%)'
  }
}));


function App() {

  const classes = useStyles();
  return (
    <ThemeProvider theme={theme} >
      <div className={classes.App}>
        <div className="App-header"></div>
        <Router>
          <Switch>
            <Route path="/" exact><Home /></Route>
            <Route path="/api-test" exact><ApiTest /></Route>
          </Switch>
        </Router>
      </div>
    </ThemeProvider>
  );
}

export default App;
