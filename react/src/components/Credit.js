import React from 'react';

function Credit(props) {
    return (
        <div className="Credit"
            style={{
            }}>
            <a href={"https://developer.yahoo.co.jp/sitemap/"}>
                <img src={"https://s.yimg.jp/images/yjdn/yjdn_attbtn2_105_17.gif"}
                    alt={"credit"}
                    style={{
                        width: "105",
                        height: "17",
                        title: "Webサービス by Yahoo! JAPAN",
                        alt: "Webサービス by Yahoo! JAPAN",
                        border: "0",
                    }} />
            </a>
        </div>
    );
}

export default Credit;