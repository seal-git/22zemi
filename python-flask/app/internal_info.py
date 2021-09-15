import requests
import os
import datetime
from app import calc_info
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from abc import ABCMeta, abstractmethod
from flask import abort
# from PIL import Image
# from io import BytesIO
from app import config


class Params:
    """
    内部で共通の検索クエリを扱うことで、APIごとに異なる検索クエリの違いを吸収する。
    このパラメータはGroupテーブルで定義されているものに対応している。(TODO: 未対応のものもまだある)
    """
    def __init__(self):
        self.query: str = None # キーワード
        self.inputtype: str = "textquery"  # textquery/phonenumber
        self.lat: float = None # 中心の緯度
        self.lon: float = None # 中心の経度
        self.max_dist: int = config.MyConfig.MAX_DISTANCE # 中心からの検索距離(m)
        self.open_day: str = None # 日付指定
        self.open_hour: str = None # 時間指定
        self.open_now: bool = False # 今開店しているか
        self.max_price: int = None # 値段の最大値(円)
        self.min_price: int = None # 値段の最小値(円)
        self.loco_mode: bool = False # Yahooロコの検索機能(ランチ、飲み放題、食べ放題、女子会、個室で検索できる)
        self.image: bool = False # 画像のあるものだけを出力
        self.results: int = config.MyConfig.STOCK_COUNT # 取得件数
        self.start: int = 0  # 取得開始位置
        self.sort: str = None # ソート順の指定

    def get_all(self):
        """
        全てのメンバを出力する

        Returns
        params : dict
        -------
        """
        params = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__"): params[key] = value
        return params

    def get_yahoo_params(self):
        # distの計算
        if self.max_dist is not None:
            dist = self.max_dist/1000
        else:
            dist = config.MyConfig.MAX_DISTANCE

        # sortのチェック
        sort_param = ["rating", "score", "hybrid", "review", "kana", "price",
                      "dist", "geo", "match"]
        sort_param += ["-"+i for i in sort_param]
        sort = self.sort if self.sort in sort_param else "hybrid"
        # boolの変換
        image = "true" if self.image else None
        loco_mode = "true" if self.loco_mode else None
        # 時間指定
        if self.open_day is not None and self.open_hour is not None:
            open = str(self.open_day) + "," + str(self.open_hour)
        else:
            open = "now"

        # パラメータをdictにして返す
        params = {
            "query": self.query,
            "results": self.results,
            "start": self.start,
            "lat": self.lat,
            "lon": self.lon,
            "sort": sort,
            "dist": dist,
            "image": image,
            "maxprice": self.max_price,
            "minprice": self.min_price,
            "loco_mode": loco_mode,
            "open": open,
        }
        return params

    def get_textsearch_params(self):
        """
        textsearch用クエリを出力する。
        query, location, radius, maxprice, minprice, regionが設定できる。
        Returns
        -------

        """
        if self.lat is not None and self.lon is not None:
            location = str(self.lat)+","+str(self.lon) # 緯度経度
        if self.max_price is not None: maxprice = min(self.max_price/2500, 4.0)
        if self.min_price is not None: minprice = min(self.min_price/2500, 4.0)
        params = {
            "query": self.query,
            "location": location,
            "radius": self.max_dist,
            "maxprice": maxprice,
            "minprice": minprice,
        }
        return params

    def get_nearbysearch_params(self):
        """
        nearbysearch用クエリを出力する。
        keyword, location, radius, maxprice, minprice, rankbyが設定できる。
        Returns
        -------
        """

        if self.lat is not None and self.lon is not None:
            location = str(self.lat)+","+str(self.lon) # 緯度経度
        if self.max_price is not None: maxprice = min(self.max_price/2500, 4.0)
        if self.min_price is not None: minprice = min(self.min_price/2500, 4.0)
        rankby = "distance" if self.sort in ["dist", "geo"] else "prominence"

        params = {
            "keyword": self.query,
            "location": location,
            "radius": self.max_dist,
            "maxprice": maxprice,
            "minprice": minprice,
            "rankby": rankby,
        }
        return params

# TODO: RestaurantInfoクラスを作る