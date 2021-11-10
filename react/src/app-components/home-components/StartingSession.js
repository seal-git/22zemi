import React from 'react'
// パッケージからインポート
import { useEffect } from "react"

function StartingSession(props) {
  useEffect(()=>{
      console.log('hello')
      props.initNewSession()
  },[])
  return (
      <div />
  )
}

export default StartingSession