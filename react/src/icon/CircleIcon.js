import React from 'react'
// パッケージからインポート
import SvgIcon from "@material-ui/core/SvgIcon";
 
export default function CircleIcon(props){
  return (
    <SvgIcon {...props}>
      <g>
        <circle class="st0" cx="12" cy="12" r="12" fill="#0070bb" stroke-width=".13187"/><path class="st1" d="m12 5.8945c-3.3758 0-6.1055 2.7297-6.1055 6.1055 0 3.3758 2.7297 6.1055 6.1055 6.1055 3.3758 0 6.1055-2.7297 6.1055-6.1055 0-3.3758-2.7297-6.1055-6.1055-6.1055zm0 9.9956c-2.1495 0-3.8901-1.7407-3.8901-3.8901 0-2.1495 1.7407-3.8901 3.8901-3.8901 2.1495 0 3.8901 1.7407 3.8901 3.8901 0 2.1495-1.7407 3.8901-3.8901 3.8901z" fill="#fff" stroke="#fff" stroke-miterlimit="10" stroke-width="4.1225e-5"/>
      </g>
    </SvgIcon>
  );
}