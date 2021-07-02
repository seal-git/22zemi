import React from 'react';
import { useRef, useEffect } from 'react';
import { CardContent } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card'
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';


const useStyles = makeStyles((theme) => ({
  // wrapper: {
  //   backgroundColor: 'transparent',
  //   margin: '5px 5px 100px 5px',
  //   height: '100%',
  // },
  cardRoot: {
    // marginBottom: '10px',
    height: '100%',
    boxSizing: "border-box",
    display: "flex",
    flexDirection: "column",
  },
  glWrapper: {
    position: "relative",
    alignItems: "center",
  },

  gridList: {
    width: '100%',
    padding: '1px',
    flex: '1',
  },

  gridListTile: {

  },

  iconButtonTop: {
    width: "100%",
    // height: "40%",
    textAlign: 'center',
    verticalAlign: "top",
    position: "absolute",
    zIndex: 1,
    top: 0,
    color: "white",
  },
  iconButtonBottom: {
    width: "100%",
    // height: "40%",
    textAlign: 'center',
    verticalAlign: "bottom",
    position: "absolute",
    zIndex: 1,
    bottom: "0",
    color: "white",
  },

  cardContent: {
    width: "100%",
    boxSizing: "border-box",
    paddingBottom: "0px",
    display: 'block',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    overflow: 'hidden',
    backgroundColor: theme.palette.background.paper,
    textAlign: 'left',
    // padding: '3px',
    // "&:last-child": {
    //   paddingBottom: '5px'
    // }
  },
  textShopName: {
    fontSize: '1.4rem',
    fontWeight: 'bold',
    whiteSpace: 'pre-wrap',
  },
  textSecondary: {
    fontSize: '1rem',
    color: '#777777',
    display: 'flex',
    whiteSpace: 'pre-line'
  },
  textStars: {
    color: '#fbc02d',
    display: 'inline-block',
    width: '40%'
  },
  space: {
    display: 'inline-block',
    margin: '0 2px',
  },
  title: {
    fontSize: 14,
  },
  pos: {
    marginBottom: 12,
  },
}));



// お店の情報を表示するコンポーネント
function RestaurantInformation(props) {
  const classes = useStyles();
  const space = <span className={classes.space}>　</span>;
  const gl = useRef(null);

  const scroll = (stepNum, scrollStep, vector) => {
    const step = scrollStep / stepNum
    gl.current.scrollTop += vector * step;
  }

  const scrollGrid = (vector) => {
    console.log(vector);
    if (gl.current.scrollHeight > gl.current.clientHeight) {
      const scrollStep = 150;
      const stepNum = 20
      for (let i = 1; i <= stepNum; i++) {
        setTimeout(() => (scroll(stepNum, scrollStep, vector)), i * 5)
      }
    }
  };

  useEffect(() => {
    console.log(gl.current);
  }, []);

  return (
    <div className="RestaurantInformation" style={props.wrapperStyle}>
      <Card variant="outlined" className={classes.cardRoot}>
        <div className={classes.glWrapper}>
          <IconButton className={classes.iconButtonTop}
                      onClick={() => {
            scrollGrid(-1)
          }}>
            ^
          </IconButton>

        <GridList
          className={classes.gridList}
          cols={props.data.Images.length <= 4 ? 1 : 2}
          spacing={2}
          ref={gl}
        >
          {props.data.Images.map((tile) => (
            <GridListTile key={tile} className={classes.gridListTile}>
              <img src={tile} />
            </GridListTile>
          ))}
        </GridList>
        <IconButton className={classes.iconButtonBottom} onClick={() => {
          scrollGrid(1)
        }}>
          v
        </IconButton>
        {/* <Divider /> */}
        </div>
        <CardContent className={classes.cardContent}>
          <Typography className={classes.textShopName}>
            {props.data.Name}
          </Typography>
          <Divider />
          <Typography className={classes.textSecondary} color="primary" >
            <span className={classes.textStars}>
              {props.data.ReviewRating}
            </span>
          </Typography>
          <Typography className={classes.textSecondary}>
            {props.data.Category == ""
              ? "カテゴリなし"
              : props.data.Category}
            {space}
            {props.data.Price == ""
              ? ""
              : "~" + props.data.Price + "円"}
            {space}{props.data.Distance}
          </Typography>
          <Typography className={classes.textSecondary} >
            {props.data.BusinessHour}
          </Typography>
        </CardContent>
      </Card>
    </div>

  );
}

export default RestaurantInformation;