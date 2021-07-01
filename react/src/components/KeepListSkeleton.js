// import React from 'react';
// import axios from "axios";
// import { Box, CardContent } from '@material-ui/core';
// import { makeStyles } from '@material-ui/core/styles';
// import { createMuiTheme } from '@material-ui/core/styles';
// import Card from '@material-ui/core/Card';
// import CardActions from '@material-ui/core/CardActions';
// import IconButton from '@material-ui/core/IconButton';
// import GridList from '@material-ui/core/GridList';
// import GridListTile from '@material-ui/core/GridListTile';
// import Divider from '@material-ui/core/Divider';
// import Typography from '@material-ui/core/Typography';

// import CloseIcon from '@material-ui/icons/Close';
// import RoomIcon from '@material-ui/icons/Room';
// import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
// import FavoriteIcon from '@material-ui/icons/Favorite';
// import Skeleton from '@material-ui/lab/Skeleton';

// const useStyles = makeStyles((theme) => ({
//     space: {
//         fontSize: '10px'
//     },
//     root: {
//         margin: '0 0 10px 0',
//         padding: '0px',
//     },
//     gridList: {
//         flexWrap: 'nowrap',
//         transform: 'translateZ(0)',
//         margin: '20px',
//         padding: '5px'
//     },
//     titleBar: {
//         background:
//             'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
//     },
//     cardContent: {
//         padding: '5px 10px'
//     },
//     cardContentSub: {
//         display: 'flex',
//         margin: '0px',
//         padding: '0px 0px',
//     },
//     cardActions: {
//         padding: '0',
//     },
//     textShopName: {
//         fontSize: '1.2rem',
//         fontWeight: 'bold'
//     },
//     textSecondary: {
//         fontSize: '1rem',
//         color: '#777777',
//         display: 'flex',
//         whiteSpace: 'pre-line'
//     },
//     textStars: {
//         color: '#fbc02d',
//         display: 'inline-block',
//         width: '40%'
//     },
//     textRecommend: {
//         display: 'inlineblock',
//         width: '60%',
//         textAlign: 'right'
//     },
//     textVotes: {
//         margin: '5px 0 0 30px',
//         padding: '5px 0 0 0',
//         textAlign: 'center',
//         fontSize: '1.2rem',
//         width: '100%',
//         backgroundColor: '#FFECC8',
//         borderTopLeftRadius: '24px',
//         borderTop: 'solid 1px #A03A00',
//         borderLeft: 'solid 1px #A03A00',
//         color: '#777777'
//     },
//     textVoteResult: {
//         fontSize: '1.4rem'
//     }
// }));

// function KeepListTile(props) {
//     const classes = useStyles();
//     const space = <span className={classes.space}>　</span>;
//     // const swichStyle = { props.mode == "Alone" ? { display: "none", } : { display: "block", } }
//     // APIにやっぱりリジェクトを送信する
//     const sendFeeling = (feeling, restaurant_id) => {
//         console.log(feeling, restaurant_id, props.userId)
//         axios.post('/api/feeling', {
//             params: {
//                 user_id: props.userId,
//                 restaurant_id: restaurant_id,
//                 feeling: feeling,
//             }
//         })
//             .then(function (response) {
//                 console.log(response)
//                 props.setListNum(response.data)
//                 props.getList()
//             })
//             .catch((error) => {
//                 console.log("error:", error);
//             });
//     }


//     return (
//         <Card variant="outlined" className={classes.root}>
//             <Skeleton variant="rect" height={100} />
//             <CardContent className={classes.cardContent}>

//                 <Typography className={classes.textShopName}>
//                     <Skeleton />
//                 </Typography>
//                 <Divider />
//                 <Typography className={classes.textSecondary} color="primary" >
//                     <Skeleton />
//                 </Typography>
//                 <Typography className={classes.textSecondary}>
//                     <Skeleton />
//                 </Typography>
//                 <Typography className={classes.textSecondary} >
//                     <Skeleton />
//                 </Typography>
//             </CardContent>
//             <Box className={classes.cardContentSub}>
//                 <CardActions className={classes.cardActions}>
//                     <IconButton >
//                         <CloseIcon />
//                     </IconButton>
//                     <IconButton>
//                         <RoomIcon />
//                     </IconButton>
//                     <IconButton >
//                         <InfoOutlinedIcon />
//                     </IconButton>
//                 </CardActions>
//                 <Typography className={classes.textVotes}>
//                     <Skeleton />
//                 </Typography>
//             </Box>
//         </Card >
//     );
// }

// export default KeepListSkeleton;