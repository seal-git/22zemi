import React from 'react';
import './App.css';
import ApiTest from './components/ApiTest'
import Home from './components/Home'
import yellow from '@material-ui/core/colors/yellow';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import { ThemeProvider } from "@material-ui/styles";
import { createMuiTheme } from '@material-ui/core/styles';
import { makeStyles } from '@material-ui/core/styles';
import { useEffect, useState } from 'react';

const theme = createMuiTheme({
  palette: {
    primary: {
      main: yellow[700],
    },
    secondary: {
      main: '#f44336',
    },
  },
});

const useStyles = makeStyles((theme) => ({
  AppAlone: {
    height: '100%',
    backgroundImage: 'linear-gradient(180.02deg, #FFEEAA 0.02%, #FDFFEB 80.2%)',
    backgroundSize: 'cover'
  },
  AppGroup: {
    height: '100%',
    backgroundImage: 'linear-gradient(180.02deg, #FFDDAA 0.02%, #FFFBEB 80.2%)'
  }
}));

function App() {
  // alone/group を抱える
  const [mode, setMode] = useState("Alone")
  const classes = useStyles();
  const [className, setClassName] = useState(classes.AppAlone)

  // モードが切り替わるとスタイルが変わる
  useEffect(() => {
    if (mode === "Alone") {
      setClassName(classes.AppAlone)
    } else if (mode === "Group") {
      setClassName(classes.AppGroup)
    }
    console.log("App:useEffect[mode]")
  }, [mode])

  return (
    <ThemeProvider theme={theme} >
      <div className={className}>
        <div className="App-header"></div>
        <Router>
          <Switch>
            <Route path="/" exact><Home mode={mode} setMode={setMode} /></Route>
            <Route path="/api-test" exact><ApiTest /></Route>
          </Switch>
        </Router>
      </div>
    </ThemeProvider>
  )
}

export default App;
