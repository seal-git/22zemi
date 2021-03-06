import requests
import os
from datetime import date, time
from app import database_functions
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from abc import ABCMeta, abstractmethod
from flask import abort
# from PIL import Image
# from io import BytesIO
from app import config
import pprint

"""
internal_info.py
検索クエリと店舗情報を内部で扱うためのクラス。
パラメータを増やしたい場合はここを増やしてからdatabase_functionsとapi_functionsをそれぞれ編集する。
"""
class Params:
    """
    内部で共通の検索クエリを扱うことで、APIごとに異なる検索クエリの違いを吸収する。
    このパラメータはGroupテーブルで定義されているものに対応している。(TODO: 未対応のものもまだある)
    """
    def __init__(self):
        self.lat: float = None  # 中心の緯度
        self.lon: float = None  # 中心の経度
        self.query: str = None  # キーワード
        self.max_dist: int = None # 中心からの検索距離(m)
        self.open_day: date = None  # 日付指定
        self.open_hour: time = None  # 時間指定
        self.open_now: bool = False  # 今開店しているか
        self.max_price: int = None  # 値段の最大値(円)
        self.min_price: int = None  # 値段の最小値(円)
        self.loco_mode: bool = False  # Yahooロコの検索機能(ランチ、飲み放題、食べ放題、女子会、個室で検索できる)
        self.image: bool = False  # 画像のあるものだけを出力
        self.results: int = config.MyConfig.STOCK_COUNT # 取得件数
        self.start: int = 0  # 取得開始位置
        self.sort: str = None  # ソート順の指定

    def set_start_and_results_from_stock(self, group_id, stock, histories_restaurants):
        """
        STOCK_COUNT個の中から選べるように、足りなければAPIで取得する
        """
        session = database_functions.get_db_session()
        self.start = session.query(Vote.restaurant).filter(Vote.group==group_id).count()
        session.close()
        self.results = stock + len(histories_restaurants) - self.start
        if self.results < 0: self.results = 0
    
    def set_start_and_results_just_responce_count(self, group_id, user_id):
        """
        レスポンスで返すぶんだけAPIで取得する
        """
        session = database_functions.get_db_session()
        self.start = config.MyConfig.RESPONSE_COUNT * (session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()).request_count, # 表示範囲：開始位置
        self.results = config.MyConfig.RESPONSE_COUNT
        session.close()


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


class RestaurantInfo:
    """
    内部で共通のレストラン情報を扱うことで、APIごとに異なるデータ構造の違いを吸収する。
    このパラメータはRestaurantテーブルで定義されているものに対応している。(TODO: 未対応のものもまだある)
    """
    def __init__(self):
        # 静的パラメーター(DBに保存するもの) -> Restaurantテーブルに保存
        self.id: str = None  # レストランID。yahoo_idとgoogle_id先に入った方。
        self.yahoo_id: str = None  # YahooのUid
        self.google_id: str = None  # Googleのplace_id
        self.name: str = None  # 店名
        self.address: str = None  # 住所
        self.lat: float = None  # 緯度
        self.lon: float = None  # 経度
        self.address: str = None  # 住所
        self.station: list[str] = []  # 駅
        self.railway: list[str] = []  # 路線
        self.phone: str = None  # 電話番号
        self.genre_name: list[str] = []  # ジャンル
        self.genre_code: list[str] = []  # ジャンル
        self.lunch_price: int = None  # ランチの値段
        self.dinner_price: int = None  # ディナーの値段
        self.monday_opening_hours: str = None  # 月曜の営業時間
        self.tuesday_opening_hours: str = None  # 火曜の営業時間
        self.wednesday_opening_hours: str = None  # 水曜の営業時間
        self.thursday_opening_hours: str = None  # 木曜の営業時間
        self.friday_opening_hours: str = None  # 金曜の営業時間
        self.saturday_opening_hours: str = None  # 土曜の営業時間
        self.sunday_opening_hours: str = None  # 日曜の営業時間
        self.access: str = None  # アクセス方法
        self.catchcopy: str = None  # キャッチコピー
        self.health_info: str = None  # 感染症対策情報
        self.web_url: str = None  # webサイトURL
        self.map_url: str = None  # 地図URL 現在地からの経路ならば動的パラメータ？
        self.yahoo_rating: list[float] = []  # 星評価のリスト
        self.yahoo_rating_float: str = None  # 星評価の平均
        self.yahoo_rating_str: str = None  # 星評価の平均を文字列で表したもの
        self.google_rating: float = None  # 星評価
        self.review: list[str] = []  # レビュー
        self.image_url: list[str] = []  # 画像のurl
        self.google_photo_reference: list[str] = []

        # 動的パラメーター(呼び出す度に計算するもの) -> Voteテーブルに保存
        self.price: int = None  # 指定時刻の値段
        self.opening_hours: str = None  # 指定時刻の営業時間
        self.distance_float: float = None  # 中心地からの距離
        self.distance_str: str = None  # 距離(文字列)
        self.votes_all: int = -1  # 投票数
        self.votes_like: int = -1  # like投票数
        self.number_of_participants: int = 0  # グループの参加人数
        self.recommend_score: float = None  # おすすめ度
        self.recommend_priority: float = -1.0 # キューの優先度


    def get_dict(self):
        """
        RestaurantInfoの情報をdictで出力

        Returns
        -------
        r_info_dict

        """
        r_info_dict = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__"):
                r_info_dict[key] = value

        return r_info_dict

    def get_dict_for_react(self):
        """
        RestaurantInfoの情報をreact用のdictで出力
        Returns
        -------

        """
        description = ''
        if self.catchcopy is not None: description += self.catchcopy + '\n'
        if self.access is not None: description += self.access + '\n'
        if self.health_info is not None: description += self.health_info + '\n'

        r_info_dict = {
            'Restaurant_id': self.id,
            'Name': self.name,
            'Distance': self.distance_str,
            'CatchCopy': description,
            'Price': self.price,
            'Address': self.address,
            'Images': self.image_url,
            'UrlWeb': self.web_url,
            'UrlMap': self.map_url,
            'ReviewRating': self.yahoo_rating_str,
            'VotesLike': self.votes_like,
            'VotesAll': self.votes_all,
            'NumberOfParticipants': self.number_of_participants,
            'RecommendScore': self.recommend_score,
            'BusinessHour': self.opening_hours,
            # TODO: 以下は導入するか別途決める
            'TopRankItem': [],
            'CassetteOwnerLogoImage': [],
            'ImagesBinary': [],
        }
        # pprint.PrettyPrinter(indent=2).pprint(r_info_dict)

        return r_info_dict
