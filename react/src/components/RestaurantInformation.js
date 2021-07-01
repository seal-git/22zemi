import React from 'react';
import { CardContent } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { Box } from "@material-ui/core";
import Card from '@material-ui/core/Card'
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';


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
  },
  cardContent: {
    width: "100%",
    display: 'block',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    overflow: 'hidden',
    backgroundColor: theme.palette.background.paper,
    textAlign: 'left',
    padding: '5px 10px',
    "&:last-child": {
      paddingBottom: '5px'
    }
  },
  textShopName: {
    fontSize: '1.4rem',
    fontWeight: 'bold'
  },
  textSecondary: {
    fontSize: '1rem',
    color: '#777777',
    display: 'flex'
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
  gridList: {
    width: '100%',
    maxHeight: '70%',
    padding: '1px',
  },
  // gridListTile: {
  //   padding: '1px'
  // },
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

  return (
    <div className="RestaurantInformation" style={props.wrapperStyle}>
      <Card variant="outlined" className={classes.cardRoot}>
        <GridList className={classes.gridList} cols={2} spacing={2}>
          {props.data.Images.map((tile) => (
            <GridListTile key={tile} className={classes.gridListTile}>
              <img src={tile} />
            </GridListTile>
          ))}
        </GridList>
        {/* <Divider /> */}
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
            {space}~{props.data.Price}円{space}{props.data.Distance}
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