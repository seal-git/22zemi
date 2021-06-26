import { CardContent } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card'
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import DirectionsWalkIcon from '@material-ui/icons/DirectionsWalk';

const useStyles = makeStyles((theme) => ({
  wrapper: {
    height: '100%',
    backgroundColor: 'transparent',
  },
  cardRoot: {
    marginBottom: '10px',
    height: '100%',
  },
  cardContent: {
    display: 'block',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    overflow: 'hidden',
    backgroundColor: theme.palette.background.paper,
    textAlign: 'left',
  },
  space: {
    display: 'inline-block',
    margin: '0 2px',
  },
  gridList: {
    width: '100%',
    height: '300px',
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
  return (
    <div className="RestaurantInformation" className={classes.wrapper}>
      <Card variant="outlined" className={classes.cardRoot}>
        <GridList className={classes.gridList} cols={2}>
          {props.data.Images.map((tile) => (
            <GridListTile key={tile} >
              <img src={tile} />
            </GridListTile>
          ))}
        </GridList>
        {/* <Divider /> */}
        <CardContent className={classes.cardContent}>

          <Typography variant="h5" component="h2">
            {props.data.Name}
          </Typography>
          <Typography className={classes.title} color="primary" gutterBottom>
            ★★★☆☆３
          </Typography>
          <Typography className={classes.title} color="textSecondary" gutterBottom>
            {props.data.Category}{space}~{props.data.Price}円
          </Typography>
          <Typography className={classes.pos} color="textSecondary">
            {props.data.Distance}m
          </Typography>
          <Typography variant="body2" component="p">
            {props.data.CatchCopy}
          </Typography>
        </CardContent>
      </Card>
    </div>

  );
}

export default RestaurantInformation;