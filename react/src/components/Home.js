import './Home.css';
import {useState} from "react"
import AppBottomNavigation from "./AppBottomNavigation"
import KeepList from "./KeepList"
import Selection from "./Selection"
import Setting from "./Setting"
import { use100vh } from 'react-div-100vh'

// ベースコンポーネントとして使う
function Home() {
    // vh単位の値を取得
    var vh = use100vh() * 0.95 * 0.01;
    console.log(vh+"px");
    // cssの--myvhの値をドキュメントのルートに設定
    document.documentElement.style.setProperty(
        '--myvh', vh+'px'
    );
  const [ view, setView ] = useState("Selection")
  const [ mode, setMode ] = useState("Alone")
  return (
    <div className="Home">
      {view==="Selection"? <Selection mode={mode} setMode={setMode} />
      : view==="KeepList"? <KeepList />
      : <Setting /> }
     <AppBottomNavigation setView={setView} />
     </ div>
  );
}

export default Home;