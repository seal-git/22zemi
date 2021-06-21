import { useState } from "react"
import AppBottomNavigation from "./AppBottomNavigation"
import Alone from './Alone'
import Group from './Group'
import Setting from "./Setting"

// ベースコンポーネントとして使う
function Home() {
  const [ view, setView ] = useState("Alone")
  return (
    <div className="Home">
      {view==="Alone"? <Alone />
      :view==="Group"? <Group />
      :<Setting />}
     <AppBottomNavigation setView={setView} />
     </ div>
  );
}

export default Home;