from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from app import config
import datetime
import requests
from random import randint

'''
データベース関連の関数
'''


def get_participants_count(group_id):
    '''
    参加人数

    Parameters
    ----------------
    group_id : int

    Returns
    ----------------
    paticipants_count : int
    '''
    return session.query(Belong).filter(Belong.group==group_id).count()

def get_histories_restaurants(group_id, user_id):
    '''
    ユーザへの送信履歴

    Parameters
    ----------------
    group_id : int
    user_id : int

    Returns
    ----------------
    restaurant_ids : [str]
    '''
    return [h.restaurant for h in session.query(History.restaurant).filter(History.group==group_id, History.user==user_id).all()]

# ============================================================================================================
# models.py


def get_lat_lon_address(query):
    '''
    Yahoo APIを使って、緯度・経度・住所を返す関数

    Parameters
    ----------------
    query : string
        場所のキーワードや住所
        例：千代田区
    
    Returns
    ----------------
    lat, lon : float
        queryで入力したキーワード周辺の緯度経度を返す
        例：lat = 35.69404120, lon = 139.75358630
    address : string
        住所

    例外処理
    ----------------
    不適切なqueryを入力した場合、Yahoo!本社の座標を返す
    '''

    geo_coder_url = "https://map.yahooapis.jp/geocode/cont/V1/contentsGeoCoder"
    params = {
        "appid": os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        "output": "json",
        "query": query
    }
    try:
        response = requests.get(geo_coder_url, params=params)
        response = response.json()
        geometry = response["Feature"][0]["Geometry"]
        coordinates = geometry["Coordinates"].split(",")
        lon = float(coordinates[0])
        lat = float(coordinates[1])
        address = response["Feature"][0]["Property"]["Address"]
    except:
        # Yahoo!本社の座標
        lon = 139.73284
        lat = 35.68001 
        address = "東京都千代田区紀尾井町1-3 東京ガ-デンテラス紀尾井町 紀尾井タワ-"
        
    return lat, lon, address


def generate_group_id():
    '''
    重複しないグループIDを生成する
    
    Returns
    ----------------
    group_id : int
    '''
    for i in range(1000000):
        group_id = randint(0, 999999)
        fetch = session.query(Group).filter(Group.id==group_id).first()
        if fetch is None:
            return group_id
    return group_id # error


def get_group_id(user_id):
    '''
    ユーザIDからグループIDを得る。グループIDを指定しない場合にはこの関数を使う。グループIDを指定する場合はユーザIDに重複があっても良いが、グループIDを指定しない場合にはユーザIDに重複があってはいけない。
    
    Parameters
    ----------------
    user_id : int
    
    Returns
    ----------------
    group_id : int
    '''
    fetch_belong = session.query(Belong.group).filter(Belong.user==user_id).first()
    if fetch_belong is not None:
        return fetch_belong.group
    else:
        return None # error


def generate_user_id():
    '''
    重複しないユーザIDを生成する
    
    Returns
    ----------------
    user_id : int
    '''
    for i in range(1000000):
        user_id = randint(0, 999999) # ''.join([random.choice(string.ascii_letters + string.digits) for j in range(12)])
        fetch = session.query(User).filter(User.id==user_id).first()
        if fetch is None:
            return user_id
    return user_id # error

def register_user_and_group_if_not_exist(group_id, user_id, place, recommend_method, api_method):
    
    # ユーザが未登録ならばデータベースに登録する
    fetch_user = session.query(User).filter(User.id==user_id).first()
    if fetch_user is None:
        new_user = User()
        new_user.id = user_id
        session.add(new_user)
        session.commit()
        print(f"new user {user_id} registered")
    
    # グループが未登録ならばデータベースに登録する
    fetch_group = session.query(Group).filter(Group.id==group_id).first()
    if fetch_group is None:
        lat,lon,address = get_lat_lon_address(place)
        new_group = Group()
        new_group.id = group_id
        new_group.lat = lat
        new_group.lon = lon
        new_group.address = address
        new_group.recommend_method = recommend_method
        new_group.api_method = api_method
        session.add(new_group)
        session.commit()
        fetch_group = session.query(Group).filter(Group.id==group_id).one()
        print(f"new group {group_id} registered")

    # 所属が未登録ならばデータベースに登録する
    fetch_belong = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).first()
    if fetch_belong is None:
        new_belong = Belong()
        new_belong.user = user_id
        new_belong.group = group_id
        session.add(new_belong)
        session.commit()
        fetch_belong = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()

    return fetch_user, fetch_group, fetch_belong

def update_feeling(group_id, user_id, restaurant_id, feeling):
    '''
    投票をデータベースに反映する
    '''
    
    # 履歴にfeelingを登録
    fetch_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==restaurant_id).first()
    if fetch_history is not None:
        prev_feeling = fetch_history.feeling
        fetch_history.feeling = feeling
        session.commit()
    else:
        # ここは実行されないはず
        print("models.py/feeling: error")
        prev_feeling = None
        new_history = History()
        new_history.group = group_id
        new_history.user = user_id
        new_history.restaurant = restaurant_id
        new_history.feeling = feeling
        session.add(new_history)
        session.commit()
    
    # 投票数を更新
    fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==restaurant_id).first()
    if fetch_vote is not None:
        fetch_vote.votes_all += 1 if prev_feeling is None else 0
        fetch_vote.votes_like += (1 if feeling else 0) if prev_feeling is None else ((0 if feeling else -1) if prev_feeling else (1 if feeling else 0))
        session.commit()
    else:
        # ここは実行されないはず
        new_vote = Vote()
        new_vote.group = group_id
        new_vote.restaurant = restaurant_id
        new_vote.votes_all = 1
        new_vote.votes_like = 1 if feeling else 0
        session.add(new_vote)
        session.commit()


def set_search_params(group_id, place, genre, query, open_day, open_hour, maxprice, minprice, sort, fetch_group=None):
    '''
    検索条件を受け取り、データベースのグループの表を更新する。
    '''
    print(f"set_filter_params renewed")

    if place is None and genre is None and query is None and open_hour is None and maxprice is None and minprice is None and sort is None: return
    
    if fetch_group is None:
        fetch_group = session.query(Group).filter(Group.id==group_id).first()

    if place is not None:
        lat,lon,address = get_lat_lon_address(place)
        fetch_group.lat = lat
        fetch_group.lon = lon
        fetch_group.address = address
    fetch_group.query = query
    fetch_group.genre = genre
    fetch_group.max_price = maxprice
    fetch_group.min_price = minprice
    if open_hour is not None:
        if open_day is not None:
            fetch_group.open_day = open_day
        else:
            fetch_group.open_day = datetime.datetime.strftime( datetime.date.today() if datetime.datetime.now().hour<=int(open_hour) else datetime.date.today() + datetime.timedelta(days=1), '%Y-%m-%d')
    else:
        fetch_group.open_day = current_timestamp()

    fetch_group.open_hour = open_hour if open_hour is not None else current_timestamp()
    if config.MyConfig.SET_OPEN_HOUR:
        fetch_group.open_hour = config.MyConfig.OPEN_HOUR

    fetch_group.sort = sort

    session.commit()

def save_histories(group_id, user_id, restaurants_info):
    '''
    ユーザの表示履歴を保存する
    '''
    for i,r in enumerate(restaurants_info):
        fetch_history = session.query(History).filter(History.group==group_id, History.user==user_id, History.restaurant==r["Restaurant_id"]).first()
        if fetch_history is None:
            new_history = History()
            new_history.group = group_id
            new_history.user = user_id
            new_history.restaurant = r["Restaurant_id"]
            new_history.feeling = None
            session.add(new_history)
            session.commit()
        
        fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==r["Restaurant_id"]).first()
        if fetch_vote is None:
            new_vote = Vote()
            new_vote.group = group_id
            new_vote.restaurant = r["Restaurant_id"]
            new_vote.votes_all = 0
            new_vote.votes_like = 0
            session.add(new_vote)
            session.commit()
        else:
            if fetch_vote.votes_all==-1:
                fetch_vote.votes_all = 0
                fetch_vote.votes_like = 0
                session.commit()

# ============================================================================================================
# api_functions.py

def save_votes(group_id, restaurants_info):

    for i,r in enumerate(restaurants_info):
        fetch_vote = session.query(Vote).filter(Vote.group==group_id, Vote.restaurant==r["Restaurant_id"]).first()
        if fetch_vote is None:
            new_vote = Vote()
            new_vote.group = group_id
            new_vote.restaurant = r["Restaurant_id"]
            new_vote.votes_all = -1
            new_vote.votes_like = -1
            session.add(new_vote)
            session.commit()

def save_restaurants_info(restaurants_info):
    '''
    restaurants_infoをデータベースに保存する

    Parameters
    ----------------
    restaurants_info : [dict]
        保存する情報
    '''

    for restaurant_info in restaurants_info:
        fetch_restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_info['Restaurant_id']).first()
        if fetch_restaurant is not None:
            fetch_restaurant.review_rating = restaurant_info.get('ReviewRating')
            fetch_restaurant.review_rating_float = restaurant_info.get('ReviewRatingFloat')
        else:
            new_restaurant = Restaurant()
            new_restaurant.id = restaurant_info['Restaurant_id']
            new_restaurant.name = restaurant_info['Name']
            new_restaurant.address = restaurant_info['Address']
            new_restaurant.lat = restaurant_info.get('Lat')
            new_restaurant.lon = restaurant_info.get('Lon')
            new_restaurant.catchcopy = restaurant_info.get('Catchcopy')
            new_restaurant.price = restaurant_info.get('Price')
            new_restaurant.lunch_price = restaurant_info.get('LunchPrice')
            new_restaurant.dinner_price = restaurant_info.get('DinnerPrice')
            new_restaurant.category = restaurant_info.get('Category')
            new_restaurant.url_web = restaurant_info.get('UrlWeb')
            new_restaurant.url_map = restaurant_info.get('UrlMap')
            new_restaurant.review_rating = restaurant_info.get('ReviewRating')
            new_restaurant.review_rating_float = restaurant_info.get('ReviewRatingFloat')
            new_restaurant.business_hour = restaurant_info.get('BusinessHour')
            new_restaurant.open_hour = restaurant_info.get('OpenHour')
            new_restaurant.close_hour = restaurant_info.get('CloseHour')
            if 'Genre' in restaurant_info:
                new_restaurant.genre_code = '\n'.join([g.get('Code') for g in restaurant_info['Genre']])
                new_restaurant.genre_name = '\n'.join([g.get('Name') for g in restaurant_info['Genre']])
            new_restaurant.images = '\n'.join(restaurant_info.get('Images'))
            new_restaurant.image_files = '\n'.join(restaurant_info.get('ImageFiles'))
            new_restaurant.image = restaurant_info.get('Image')
            new_restaurant.menu = restaurant_info.get('Menu')
            session.add(new_restaurant)
            session.commit()


def convert_restaurants_info_from_fetch_restaurants(f_restaurant):
    restaurant_info = {}
    restaurant_info['Restaurant_id'] = f_restaurant.id
    restaurant_info['Name'] = f_restaurant.name
    restaurant_info['Address'] = f_restaurant.address
    restaurant_info['Lat'] = f_restaurant.lat
    restaurant_info['Lon'] = f_restaurant.lon
    restaurant_info['Catchcopy'] = f_restaurant.catchcopy
    restaurant_info['Price'] = f_restaurant.price
    restaurant_info['LunchPrice'] = f_restaurant.lunch_price
    restaurant_info['DinnerPrice'] = f_restaurant.dinner_price
    restaurant_info['Category'] = f_restaurant.category
    restaurant_info['UrlWeb'] = f_restaurant.url_web
    restaurant_info['UrlMap'] = f_restaurant.url_map
    restaurant_info['ReviewRating'] = f_restaurant.review_rating
    restaurant_info['ReviewRatingFloat'] = f_restaurant.review_rating_float
    restaurant_info['BusinessHour'] = f_restaurant.business_hour
    restaurant_info['OpenHour'] = f_restaurant.open_hour
    restaurant_info['CloseHour'] = f_restaurant.close_hour
    restaurant_info['Genre'] = [{'Code':c, 'Name':n} for c,n in zip(f_restaurant.genre_code.split('\n'), f_restaurant.genre_name.split('\n'))]
    restaurant_info['Images'] = f_restaurant.images.split('\n')
    restaurant_info['ImageFiles'] = f_restaurant.image_files.split('\n')
    restaurant_info['Image'] = f_restaurant.image
    restaurant_info['Menu'] = f_restaurant.menu
    return restaurant_info


def load_stable_restaurants_info(restaurant_ids):
    '''
    データベースからrestaurants_infoを取得

    Parameters
    ----------------
    restaurant_ids : [string]
        レストランIDのリスト
    
    Returns
    ----------------
    restaurants_info : [dict]
        レスポンスするレストラン情報を返す。
    '''
    print(f"load_restaurants_info: load {len(restaurant_ids)} items")
    restaurants_info = [None for rid in restaurant_ids]
    fetch_restaurants = session.query(Restaurant).filter(Restaurant.id.in_(restaurant_ids)).all()
    for f_restaurant in fetch_restaurants:
        restaurant_info = convert_restaurants_info_from_fetch_restaurants(f_restaurant)
        restaurants_info[ restaurant_ids.index(f_restaurant.id) ] = restaurant_info
    
    return restaurants_info