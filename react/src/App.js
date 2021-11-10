import React from 'react'
import './css/App.css'
// パッケージからインポート
import yellow from '@material-ui/core/colors/yellow'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'
import { ThemeProvider } from "@material-ui/styles"
import { createMuiTheme } from '@material-ui/core/styles'
import { makeStyles } from '@material-ui/core/styles'
import { useEffect, useState } from 'react'
// 他のファイルからインポート
import Home from './app-components/Home'

const theme = createMuiTheme({
  palette: {
    primary: {
      main: yellow[700],
    },
    secondary: {
      main: '#f44336',
    },
  },
  typography:{
    fontFamily: ['"Noto Sans JP"', '"Hiragino Kaku Gothic ProN"', 'Meiryo', 'sans-serif' ].join(','),
    fontWeight: 'bold',
  },
});

const useStyles = makeStyles((theme) => ({
  App: {
    height: '100%',
    // backgroundImage: 'linear-gradient(180.02deg, #FFEEAA 0.02%, #FDFFEB 80.2%)',
    // backgroundSize: 'cover'
  },
}));

function App() {
  const classes = useStyles();
  const [className, setClassName] = useState(classes.App)

  return (
    <ThemeProvider theme={theme} >
      <div className={className}>
        <div className="App-header"></div>
        <Router>
          <Switch>
            <Route path="/"><Home/></Route>
          </Switch>
        </Router>
      </div>
    </ThemeProvider>
  )
}

export default App
