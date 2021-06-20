import { useState } from "react"
import axios from 'axios';
import Setting from "./Setting";
import AppBottomNavigation from "./AppBottomNavigation"

// ひとりで決める
function Alone() {
  const [ conditions, setConditions ] = useState({'isSet':false})
  const [ view, setView ] = useState("Swipe")

  return (
    <div className="Alone">
      {conditions['isSet'] ?
        (view==="KeepList"?
        <div><h1>キープリスト予定地</h1></div> :
        <div><h1>工事中</h1></div>
      ): 
      <Setting setConditions={ setConditions }/>}
    
      {conditions['isSet'] && <AppBottomNavigation setView={setView}/>}
    </div>
  );
}

export default Alone;
