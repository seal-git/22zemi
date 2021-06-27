import {useState} from "react"
import {makeStyles} from '@material-ui/core/styles';
import AppBottomNavigation from "./AppBottomNavigation"
import KeepList from "./KeepList"
import Selection from "./Selection"
import Setting from "./Setting"
import "./Home.css"

const produceId = () =>{
  return Math.random().toString(32).substring(2)
}
// ベースコンポーネントとして使う
function Home(props) {
  // view を抱える。背景操作の都合で mode は上位コンポーネント App に持たせる
  const [view, setView] = useState("Selection")
  // ユーザID、グループIDを抱える。現状自前で用意しているがAPIに要求できるほうが嬉しい
  const [userId, setUserId] = useState(produceId())
  const [groupId, setGroupId] = useState(produceId())

  const turnMode = (groupId) => {
    // mode を反転させる
    if (props.mode === "Group") {
      props.setMode('Alone')
    } else if (props.mode === "Alone") {
      props.setMode('Group')
    } else {
      console.log("Home:turnMode:undefined mode")
      return;
    }

    // userID はモードが変わるごとに作り直す？
    setUserId(produceId())

    // groupId が指定されていない場合システム側で用意する
    // 指定されている場合はそのIDを使う
    if(groupId===undefined || groupId===""){
      setGroupId(produceId())
    }else{
      setGroupId(groupId)
    }
  };

  return (
        <div className="Home">
            <div className="Content">
                {view === "Selection" ? 
                <Selection 
                  userId={userId}
                  groupId={groupId}
                  mode={props.mode} 
                  setMode={props.setMode} 
                  turnMode={turnMode} 
                />
                    : view === "KeepList" ? <KeepList/>
                        : <Setting mode={props.mode} turnMode={turnMode} setView={setView}/>}
            </div>
            <AppBottomNavigation view={view} setView={setView}/>
        </ div>
    );
}

export default Home;