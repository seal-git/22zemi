import { Box, CardContent } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import { createMuiTheme } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import IconButton from '@material-ui/core/IconButton';
import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';
import Divider from '@material-ui/core/Divider';
import Typography from '@material-ui/core/Typography';

import CloseIcon from '@material-ui/icons/Close';
import RoomIcon from '@material-ui/icons/Room';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import FavoriteIcon from '@material-ui/icons/Favorite';

const useStyles = makeStyles((theme) => ({
    space: {
        fontSize: '10px'
    },
    root: {
        margin: '0 0 10px 0',
        padding: '0px',
    },
    gridList: {
        flexWrap: 'nowrap',
        transform: 'translateZ(0)',
        margin: '20px',
        padding: '5px'
    },
    titleBar: {
        background:
            'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
    },
    cardContent: {
        padding: '5px 10px'
    },
    cardContentSub: {
        display: 'flex',
        margin: '0px',
        padding: '0px 0px',
    },
    cardActions: {
        padding: '0',
    },
    textShopName: {
        fontSize: '1.2rem',
        fontWeight: 'bold'
    },
    textSecondary: {
        fontSize: '0.8rem',
        color: '#777777',
        display: 'flex'
    },
    textStars: {
        color: '#fbc02d',
        display: 'inline-block',
        width: '40%'
    },
    textRecommend: {
        display: 'inlineblock',
        width: '60%',
        textAlign: 'right'
    },
    textVotes: {
        margin: '5px 0 0 30px',
        padding: '5px 0 0 0',
        textAlign: 'center',
        fontSize: '1.2rem',
        width: '100%',
        backgroundColor: '#FFECC8',
        borderTopLeftRadius: '24px',
        borderTop: 'solid 1px #A03A00',
        borderLeft: 'solid 1px #A03A00',
        color: '#777777'
    },
    textVoteResult: {
        fontSize: '1.4rem'
    }
}));

function KeepListTile(props) {
    const classes = useStyles();
    const space = <span className={classes.space}>　</span>;
    const text = "hello\nhello";

    return (
        <Card variant="outlined" className={classes.root}>

            <GridList className={classes.gridList} cols={2.5} cellHeight={100}>
                {props.data.Images.map((tile) => (
                    <GridListTile key={tile} className={classes.gridListTile}>
                        <img src={tile} />
                    </GridListTile>
                ))}
            </GridList>
            <CardContent className={classes.cardContent}>

                <Typography className={classes.textShopName}>
                    {props.data.Name}
                </Typography>
                <Divider />
                <Typography className={classes.textSecondary} color="primary" >
                    <span className={classes.textStars}>
                        {/* ☆☆☆☆☆　0 */}
                        {props.data.ReviewRating}
                    </span>
                    <span className={classes.textRecommend}>
                        あなたへのおすすめ度{props.data.RecommendScore}%
                    </span>
                </Typography>
                <Typography className={classes.textSecondary}>
                    {props.data.Category == ""
                        ? "カテゴリ未分類"
                        : props.data.Category}
                    {space}~{props.data.Price}円{space}{props.data.Distance}
                </Typography>
                <Typography className={classes.textSecondary} >
                    {props.data.BusinessHour}
                </Typography>
            </CardContent>
            <Box className={classes.cardContentSub}>
                <CardActions className={classes.cardActions}>
                    <IconButton>
                        <CloseIcon />
                    </IconButton>
                    <IconButton onClick={(e) => {
                        e.preventDefault();
                        window.open(props.data.UrlYahooMap, '_blank');
                    }}>
                        <RoomIcon />
                    </IconButton>
                    <IconButton onClick={(e) => {
                        e.preventDefault();
                        window.open(props.data.UrlYahooLoco, '_blank')
                    }}>
                        <InfoOutlinedIcon />
                    </IconButton>
                </CardActions>
                <Typography className={classes.textVotes}>
                    <FavoriteIcon style={{ fontSize: 18 }} />
                    <span className={classes.textVoteResult}>{props.data.VotesLike}</span>
                    /{props.data.VotesAll}
                </Typography>
            </Box>
        </Card >
    );
}

export default KeepListTile;