import { useState } from "react";
import Buttons from "./Buttons";
import RestaurantInformation from "./RestaurantInformation";

// ひとりで決める
function Alone() {
  // サンプルデータを使ったプロトタイピング
  // 実際にはAPIからデータを得る
  const [idx, setIndex] = useState(0)
  const samples = [
    {
      "name": "神鶏 市ヶ谷店",
      "mapURL": "https://map.yahoo.co.jp/route/train?from=%E5%9B%9B%E3%83%84%E8%B0%B7%E9%A7%85&to=%E6%9D%B1%E4%BA%AC%E9%83%BD%E6%96%B0%E5%AE%BF%E5%8C%BA%E5%B8%82%E8%B0%B7%E7%94%B0%E7%94%BA1-3-5&t=1&y=202106&d=20&h=20&m=44&sort=1&lat=35.68754&lon=139.73242&zoom=15&maptype=basic",
      "reserveURL":"https://loco.yahoo.co.jp/place/g-8c8pQERfq2g/"
    },
    {
      "name": "一軒家イタリアン ＥＬＳＡ 新宿本店",
      "mapURL": "https://map.yahoo.co.jp/route/train?from=%E5%9B%9B%E3%83%84%E8%B0%B7%E9%A7%85&to=%E6%9D%B1%E4%BA%AC%E9%83%BD%E6%96%B0%E5%AE%BF%E5%8C%BA%E6%96%B0%E5%AE%BF3-10-5&t=1&y=202106&d=20&h=20&m=44&sort=1&lat=35.68604&lon=139.71303&zoom=16&maptype=basic",
      "reserveURL": "https://loco.yahoo.co.jp/place/g-1dIwmpfPtko"
    },
  ]
  const [data, setData] = useState(samples[0])

  // 各ボタンに対応する関数
  const reject = () => {
    console.log("reject")
    const nextIdx = 1 - idx
    setIndex(nextIdx)
    setData(samples[nextIdx])
  }
  const keep = () => {
    console.log("keep")
    const nextIdx = 1 - idx
    setIndex(nextIdx)
    setData(samples[nextIdx])
  }
  const direct = () => {
    console.log("direct")
    window.open(data.mapURL)
  }
  const reserve = () => {
    console.log("reserve")
    window.open(data.reserveURL);
  }
  return (
    <div className="Alone">
        <RestaurantInformation data={data}/>
        <Buttons reject={reject} keep={keep} direct={direct} reserve={reserve}/>
    </div>
  );
}

export default Alone;
