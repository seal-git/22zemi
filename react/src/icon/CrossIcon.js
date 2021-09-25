import React from 'react'
// パッケージからインポート
import SvgIcon from "@material-ui/core/SvgIcon";

// 他ファイルからインポート
 
export default function CrossIcon(props){
  return (
    <SvgIcon {...props}>
      <circle cx="12" cy="12" r="12" fill="#d90060"/>
      <path d="M14.48 12l2.478-2.48a1.608 1.608 0 000-2.28l-.198-.198a1.608 1.608 0 00-2.28 0L12 9.52 9.52 7.04a1.608 1.608 0 00-2.28 0l-.198.199a1.608 1.608 0 000 2.28L9.52 12l-2.48 2.48a1.608 1.608 0 000 2.28l.199.198a1.608 1.608 0 002.28 0L12 14.48l2.48 2.48a1.608 1.608 0 002.28 0l.198-.199a1.608 1.608 0 000-2.28z" fill="#fff"/>
    </SvgIcon>
  );
}