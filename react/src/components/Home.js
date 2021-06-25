import { useState } from "react"
import { makeStyles } from '@material-ui/core/styles';
import AppBottomNavigation from "./AppBottomNavigation"
import KeepList from "./KeepList"
import Selection from "./Selection"
import Setting from "./Setting"

// ベースコンポーネントとして使う
function Home() {
  const [view, setView] = useState("Selection")
  const [mode, setMode] = useState("Alone")
  return (
    <div className="Home">
      {view === "Selection" ? <Selection mode={mode} setMode={setMode} />
        : view === "KeepList" ? <KeepList />
          : <Setting />}
      <AppBottomNavigation setView={setView} />
    </ div>
  );
}

export default Home;