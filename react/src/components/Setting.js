
import { Button } from "@material-ui/core"

// 設定用コンポーネント 
// 設定項目は要議論
function Setting(props) {
  const handleStartButton = () => {
    const conditions = {"isSet":true, "user_id":1}
    props.setConditions(conditions)
  }
  return (
    <div className="Setting">
      <h1>Setting</h1>
      <Button variant="contained" color="primary" onClick={ ()=>{ handleStartButton(); } }>お店を探す</Button>
    </div>
  );
}

export default Setting;
