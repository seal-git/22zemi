import { CardContent } from '@material-ui/core';
import Card from '@material-ui/core/Card'

import sample1 from './sample1.png'
import sample2 from './sample2.png'

const style1 = {
  width: '100%',
  height: '20rem',
  backgroundImage: `url(${sample1})`
};
const style2 = {
  width: '100%',
  height: '20rem',
  backgroundImage: `url(${sample2})`
};

// お店の情報を表示するコンポーネント
function RestaurantInformation(props) {
    return(
        <div className="RestaurantInformation">
        <Card variant="outlined">
            <CardContent>
            {props.data["name"]==="神鶏 市ヶ谷店"
            ?  <img style={ style1 } />
            : <img style={ style2 } /> }
            {props.data["name"]}
            </CardContent>
        </Card>
        </div>

    );
}

export default RestaurantInformation;