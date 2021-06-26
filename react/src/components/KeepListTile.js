import { CardContent } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card'
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';

import GridListTileBar from '@material-ui/core/GridListTileBar';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
    tile: {
        margin: '10px'
    },
    root: {
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-around',
        overflow: 'hidden',
        backgroundColor: theme.palette.background.paper,
    },
    gridList: {
        flexWrap: 'nowrap',
        // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
        transform: 'translateZ(0)',
    },
    title: {
        color: theme.palette.primary.light,
    },
    titleBar: {
        background:
            'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
    },
}));



function KeepListTile(props) {
    const classes = useStyles();
    const space = <span className={classes.space}>　</span>;

    return (
        <Card variant="outlined" className={classes.tile}>
            {/* <GridList cellHeight={160} rows={1}>
                {props.data.Images.map((tile) => (
                    <GridListTile key={tile}>
                        <img src={tile} className={classes.tileImg} />
                    </GridListTile>
                ))}
            </GridList> */}

            <GridList className={classes.gridList} cols={2.5}>
                {props.data.Images.map((tile) => (
                    <GridListTile key={tile}>
                        <img src={tile} />
                        <GridListTileBar
                            // title={tile.title}
                            classes={{
                                root: classes.titleBar,
                                title: classes.title,
                            }}
                        // actionIcon={
                        //     <IconButton aria-label={`star ${tile.title}`}>
                        //         <StarBorderIcon className={classes.title} />
                        //     </IconButton>
                        // }
                        />
                    </GridListTile>
                ))}
            </GridList>
            <CardContent className={classes.cardContent}>

                <Typography component="h2">
                    {props.data.Name}
                </Typography>
                <Typography className={classes.title} color="primary" component="h4" gutterBottom>
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
    );
}

export default KeepListTile;