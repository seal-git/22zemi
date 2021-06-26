import { useState } from "react"
import { makeStyles } from '@material-ui/core/styles';
import AppBottomNavigation from "./AppBottomNavigation"
import KeepList from "./KeepList"
import Selection from "./Selection"
import Setting from "./Setting"

const useStyles = makeStyles({
  Home: {
  },
});
const produceId = () =>{
  return Math.random().toString(32).substring(2)
}

// ベースコンポーネントとして使う
function Home(props) {
  const [view, setView] = useState("Selection")
  const [userId, setUserId] = useState(produceId())
  console.log('userId',userId)
  const [groupId, setGroupId] = useState("--")

  const turnMode = (groupId) => {
    if (props.mode === "Group") {
      props.setMode('Alone')
      setUserId(produceId())
    } else if (props.mode === "Alone") {
      props.setMode('Group')
      setUserId(produceId())
    }
    setGroupId(groupId)
  };

  const classes = useStyles()
  return (
    <div className={classes.Home}>
      {view === "Selection" ? <Selection mode={props.mode} turnMode={turnMode} userId={userId} groupId={groupId}/>
        : view === "KeepList" ? <KeepList userId={userId} groupId={groupId} />
          : <Setting mode={props.mode} turnMode={turnMode} setView={setView}/>}
      <AppBottomNavigation setView={setView} />
    </ div>
  );
}

export default Home;