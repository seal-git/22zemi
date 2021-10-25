import React from 'react'
// パッケージからインポート
import { useEffect } from "react"

function CallingInvite(props) {

  useEffect(()=>{
      console.log('hello')
      props.initNewSession()
  },[])
  return (
      <div />
  )
}

export default CallingInvite