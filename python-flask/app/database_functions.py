from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
from app.internal_info import *
from app import config, api_functions
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


def register_user_and_group_if_not_exist(group_id, user_id, recommend_method, api_method):
    
    # ユーザが未登録ならばデータベースに登録する
    fetch_user = session.query(User).filter(User.id==user_id).first()
    if fetch_user is None:
        new_user = User()
        new_user.id = user_id
        session.add(new_user)
        session.commit()
        print(f"new user {user_id} registered")
    
    # グループが未登録ならばデータベースに登録する
    first_time_group_flg = False
    fetch_group = session.query(Group).filter(Group.id==group_id).first()
    if fetch_group is None:
        new_group = Group()
        new_group.id = group_id
        new_group.recommend_method = recommend_method
        new_group.api_method = api_method
        session.add(new_group)
        session.commit()
        first_time_group_flg = True
        fetch_group = session.query(Group).filter(Group.id==group_id).one()
        print(f"new group {group_id} registered")

    # 所属が未登録ならばデータベースに登録する
    first_time_belong_flg = False
    fetch_belong = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).first()
    if fetch_belong is None:
        new_belong = Belong()
        new_belong.user = user_id
        new_belong.group = group_id
        session.add(new_belong)
        session.commit()
        first_time_belong_flg = True
        fetch_belong = session.query(Belong).filter(Belong.group==group_id, Belong.user==user_id).one()

    return fetch_user, fetch_group, fetch_belong, first_time_group_flg, first_time_belong_flg

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
    fetch_vote = session.query(Vote).filter(Vote.group==group_id,
                                            Vote.restaurant==restaurant_id
                                            ).first()
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


def set_search_params(group_id, params, fetch_group=None):
    '''
    検索条件を受け取り、データベースのグループの表を更新する。
    '''
    print(f"set_filter_params renewed")


    if fetch_group is None:
        fetch_group = session.query(Group).filter(Group.id==group_id).first()

    fetch_group.lat = params.lat
    fetch_group.lon = params.lon
    fetch_group.query = params.query
    fetch_group.max_dist = params.max_dist
    if params.open_day is None:
        fetch_group.open_day = None
    else:
        today = datetime.date.today()
        month = today.month if today.day <= int(params.open_day) else today.month + 1
        year = today.year if month <= 12 else today.year + 1
        fetch_group.open_day = datetime.date(year, month, int(params.open_day))
    if params.open_hour is None:
        fetch_group.open_hour = None
    else:
        hoursecond = params.open_hour.split(':')
        fetch_group.open_hour = datetime.time(hour=int(hoursecond[0]), second=int(hoursecond[1]))
    fetch_group.open_now = params.open_now
    fetch_group.max_price = params.max_price
    fetch_group.min_price = params.min_price
    fetch_group.loco_mode = params.loco_mode
    fetch_group.image = params.image
    fetch_group.results = params.results
    fetch_group.start = params.start
    fetch_group.sort = params.sort

    session.commit()

def save_histories(group_id, user_id, restaurants_info):
    '''
    ユーザの表示履歴を保存する
    '''
    for i,r in enumerate(restaurants_info):
        fetch_history = session.query(History).filter(History.group==group_id,
                                                      History.user==user_id,
                                                      History.restaurant==r.id
                                                      ).first()
        if fetch_history is None:
            new_history = History()
            new_history.group = group_id
            new_history.user = user_id
            new_history.restaurant = r.id
            new_history.feeling = None
            session.add(new_history)
            session.commit()
        
        fetch_vote = session.query(Vote).filter(Vote.group==group_id,
                                                Vote.restaurant==r.id
                                                ).first()
        if fetch_vote is None:
            new_vote = Vote()
            new_vote.group = group_id
            new_vote.restaurant = r.id
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
        fetch_vote = session.query(Vote).filter(
            Vote.group == group_id, Vote.restaurant == r.id
                                ).with_for_update().first()
        if fetch_vote is None:
            fetch_vote = Vote()
            fetch_vote.group = group_id
            fetch_vote.restaurant = r.id

        fetch_vote.votes_like = r.votes_like
        fetch_vote.votes_all = r.votes_all
        fetch_vote.number_of_participants = r.number_of_participants
        fetch_vote.recommend_priority = r.number_of_participants
        fetch_vote.price = r.price
        fetch_vote.opening_hours = r.opening_hours
        fetch_vote.distance_float = r.distance_float
        fetch_vote.distance_str = r.distance_str
        fetch_vote.recommend_score = r.recommend_score

        session.add(fetch_vote)
        session.commit()
    return

def save_restaurants(restaurants_info):
    '''
    restaurants_infoをデータベースに保存する

    Parameters
    ----------------
    restaurants_info : [dict]
        保存する情報
    '''

    for r_info in restaurants_info:
        fetch_restaurant = session.query(Restaurant).filter(
            Restaurant.id==r_info.id).with_for_update().first()

        if fetch_restaurant is None:
            fetch_restaurant = Restaurant()
            fetch_restaurant.id = r_info.id

        fetch_restaurant.yahoo_id = r_info.yahoo_id
        fetch_restaurant.google_id = r_info.google_id
        fetch_restaurant.name = r_info.name
        fetch_restaurant.address = r_info.address
        fetch_restaurant.lat = r_info.lat
        fetch_restaurant.lon = r_info.lon
        fetch_restaurant.station = '\n'.join(r_info.station)
        fetch_restaurant.railway = '\n'.join(r_info.railway)
        fetch_restaurant.phone = r_info.phone
        fetch_restaurant.genre_name = '\n'.join(r_info.genre_name)
        fetch_restaurant.genre_code = '\n'.join(r_info.genre_code)
        fetch_restaurant.lunch_price = r_info.lunch_price
        fetch_restaurant.dinner_price = r_info.dinner_price
        fetch_restaurant.monday_opening_hours = r_info.monday_opening_hours
        fetch_restaurant.tuesday_opening_hours = r_info.tuesday_opening_hours
        fetch_restaurant.wednesday_opening_hours = r_info.wednesday_opening_hours
        fetch_restaurant.thursday_opening_hours = r_info.thursday_opening_hours
        fetch_restaurant.friday_opening_hours = r_info.friday_opening_hours
        fetch_restaurant.saturday_opening_hours = r_info.saturday_opening_hours
        fetch_restaurant.sunday_opening_hours = r_info.sunday_opening_hours
        fetch_restaurant.access = r_info.access
        fetch_restaurant.catchcopy = r_info.catchcopy
        fetch_restaurant.health_info = r_info.health_info
        fetch_restaurant.web_url = r_info.web_url
        fetch_restaurant.map_url = r_info.map_url
        fetch_restaurant.yahoo_rating_float = r_info.yahoo_rating_float
        fetch_restaurant.yahoo_rating_str = r_info.yahoo_rating_str
        fetch_restaurant.google_rating = r_info.google_rating
        fetch_restaurant.review = '\t'.join(r_info.review)
        fetch_restaurant.image_url = '\n'.join(r_info.image_url)

        session.add(fetch_restaurant)
        session.commit()

        # print(f"save_restaurants_info: saved {fetch_restaurant.id}   ")
    return


def get_restaurant_info_from_db(restaurant_id, group_id):
    f_restaurant = session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    f_votes = session.query(Vote).filter(Vote.group == group_id,
                                         Vote.restaurant == restaurant_id
                                         ).first()
    restaurant_info = RestaurantInfo()
    restaurant_info.id = f_restaurant.id
    restaurant_info.yahoo_id = f_restaurant.yahoo_id
    restaurant_info.google_id = f_restaurant.google_id
    restaurant_info.name = f_restaurant.name
    restaurant_info.address = f_restaurant.address
    restaurant_info.lat = f_restaurant.lat
    restaurant_info.lon = f_restaurant.lon
    restaurant_info.station = f_restaurant.station.split('\n')
    restaurant_info.railway = f_restaurant.railway.split('\n')
    restaurant_info.phone = f_restaurant.phone
    restaurant_info.genre_code = f_restaurant.genre_code
    restaurant_info.genre_name = f_restaurant.genre_name
    restaurant_info.lunch_price = f_restaurant.lunch_price
    restaurant_info.dinner_price = f_restaurant.dinner_price
    restaurant_info.monday_opening_hours = f_restaurant.monday_opening_hours
    restaurant_info.tuesday_opening_hours = f_restaurant.tuesday_opening_hours
    restaurant_info.wednesday_opening_hours = f_restaurant.wednesday_opening_hours
    restaurant_info.thursday_opening_hours = f_restaurant.thursday_opening_hours
    restaurant_info.friday_opening_hours = f_restaurant.friday_opening_hours
    restaurant_info.saturday_opening_hours = f_restaurant.saturday_opening_hours
    restaurant_info.sunday_opening_hours = f_restaurant.sunday_opening_hours
    restaurant_info.access = f_restaurant.access
    restaurant_info.catchcopy = f_restaurant.catchcopy
    restaurant_info.health_info = f_restaurant.health_info
    restaurant_info.web_url = f_restaurant.web_url
    restaurant_info.map_url = f_restaurant.map_url
    # restaurant_info.yahoo_rating = f_restaurant.yahoo_rating TODO
    restaurant_info.yahoo_rating_float = f_restaurant.yahoo_rating_float
    restaurant_info.yahoo_rating_str = f_restaurant.yahoo_rating_str
    restaurant_info.google_rating = f_restaurant.google_rating
    restaurant_info.review = f_restaurant.review.split('\t')
    restaurant_info.image_url = f_restaurant.image_url.split('\n')

    restaurant_info.price = f_votes.price
    restaurant_info.opening_hours = f_votes.opening_hours
    restaurant_info.distance_float = f_votes.distance_float
    restaurant_info.distance_str = f_votes.distance_str
    restaurant_info.votes_all = f_votes.votes_all
    restaurant_info.votes_like = f_votes.votes_like
    restaurant_info.number_of_participants = f_votes.number_of_participants
    restaurant_info.recommend_score = f_votes.recommend_score
    restaurant_info.recommend_priority = f_votes.recommend_priority
    return restaurant_info


def load_restaurants_info(restaurant_ids, group_id):
    '''
    データベースからrestaurants_infoを取得

    Parameters
    ----------------
    restaurant_ids : [string]
        レストランIDのリスト
    
    Returns
    ----------------
    restaurants_info : [RestaurantInfo]
        レスポンスするレストラン情報を返す。
    '''
    if len(restaurant_ids) == 0:
        return []
    restaurants_info = [None for rid in restaurant_ids]
    for rid in restaurant_ids:
        restaurant_info = get_restaurant_info_from_db(rid, group_id)
        restaurants_info[restaurant_ids.index(rid)] = restaurant_info
    
    return restaurants_info

def get_search_params_from_fetch_group(fetch_group):
    '''
    ユーザが指定した検索条件からAPIで使用する検索条件を取得
    return: params: 内部で定義したパラメータ
    '''
    params = Params()


    params.lat = fetch_group.lat
    params.lon = fetch_group.lon
    if fetch_group.query is not None: params.query = fetch_group.query
    params.max_dist = fetch_group.max_dist
    if fetch_group.open_hour is not None: params.open_hour = fetch_group.open_hour
    if fetch_group.open_hour is not None: params.open_day = fetch_group.open_day
    if fetch_group.open_now is not None: params.open_now = fetch_group.open_now
    params.max_price = fetch_group.max_price
    params.min_price = fetch_group.min_price
    params.loco_mode = fetch_group.loco_mode
    params.image = fetch_group.image
    params.results = fetch_group.results
    params.start = fetch_group.start
    params.sort = fetch_group.sort

    return params


def set_start():
    # TODO: 実装
    # startを更新する
    pass

