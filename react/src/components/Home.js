import {useState} from "react"
import {makeStyles} from '@material-ui/core/styles';
import AppBottomNavigation from "./AppBottomNavigation"
import KeepList from "./KeepList"
import Selection from "./Selection"
import Setting from "./Setting"
import "./Home.css"

// ベースコンポーネントとして使う
function Home() {
    const [view, setView] = useState("Selection")
    const [mode, setMode] = useState("Alone")
    return (
        <div className="Home">
            <div className="Content">
                {view === "Selection" ? <Selection mode={mode} setMode={setMode}/>
                    : view === "KeepList" ? <KeepList/>
                        : <Setting/>}
            </div>
            <AppBottomNavigation setView={setView}/>
        </ div>
    );
}

export default Home;