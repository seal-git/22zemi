from geopy.distance import great_circle
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote

'''

api_functionsで使う情報を計算する

'''


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
        if fetch_restaurant is None:
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
            new_restaurant.url_yahoo_loco = restaurant_info.get('UrlYahooLoco')
            new_restaurant.url_yahoo_map = restaurant_info.get('UrlYahooMap')
            new_restaurant.review_rating = restaurant_info.get('ReviewRating')
            new_restaurant.business_hour = restaurant_info.get('BusinessHour')
            new_restaurant.open_hour = restaurant_info.get('OpenHour')
            new_restaurant.close_hour = restaurant_info.get('CloseHour')
            if 'Genre' in restaurant_info:
                new_restaurant.genre_code = '\n'.join([g.get('Code') for g in restaurant_info['Genre']])
                new_restaurant.genre_name = '\n'.join([g.get('Name') for g in restaurant_info['Genre']])
            new_restaurant.images = '\n'.join(restaurant_info.get('Images'))
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
    restaurant_info['UrlYahooLoco'] = f_restaurant.url_yahoo_loco
    restaurant_info['UrlYahooMap'] = f_restaurant.url_yahoo_map
    restaurant_info['ReviewRating'] = f_restaurant.review_rating
    restaurant_info['BusinessHour'] = f_restaurant.business_hour
    restaurant_info['OpenHour'] = f_restaurant.open_hour
    restaurant_info['CloseHour'] = f_restaurant.close_hour
    restaurant_info['Genre'] = [{'Code':c, 'Name':n} for c,n in zip(f_restaurant.genre_code.split('\n'), f_restaurant.genre_name.split('\n'))]
    restaurant_info['Images'] = f_restaurant.images.split('\n')
    restaurant_info['Image'] = f_restaurant.image
    restaurant_info['Menu'] = f_restaurant.menu
    return restaurant_info


def load_restaurants_info(restaurant_ids):
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
    restaurants_info = [None for rid in restaurant_ids]
    fetch_restaurants = session.query(Restaurant).filter(Restaurant.id.in_(restaurant_ids)).all()
    for f_restaurant in fetch_restaurants:
        restaurant_info = convert_restaurants_info_from_fetch_restaurants(f_restaurant)
        restaurants_info[ restaurant_ids.index(f_restaurant.id) ] = restaurant_info
    
    return restaurants_info


def add_votes_distance(fetch_group, group_id, restaurants_info):
    '''
    restaurants_infoに投票数と現在位置からの距離を加える

    Parameters
    ----------------
    fetch_group : 
        データベースのグループ情報
    group_id : int
        グループID
    restaurants_info : [dict]
        レストランIDのリスト
    
    Returns
    ----------------
    restaurants_info : [dict]
        レスポンスするレストラン情報を返す。
    '''
    for i in range(len(restaurants_info)):
        restaurants_info[i]['VotesLike'] = session.query(History).filter(History.group==group_id, History.restaurant==restaurants_info[i]['Restaurant_id'], History.feeling==True).count() # レストランのいいね数
        restaurants_info[i]['VotesAll'] = session.query(History).filter(History.group==group_id, History.restaurant==restaurants_info[i]['Restaurant_id'], History.feeling is not None).count() # レストランの投票人数
        restaurants_info[i]['NumberOfParticipants'] = str(session.query(Belong).filter(Belong.group==group_id).count()) # グループの参加人数
        restaurants_info[i]["distance_float"] = great_circle((fetch_group.lat, fetch_group.lon), (restaurants_info[i]['Lat'], restaurants_info[i]['Lon'])).m #距離 メートル float
        restaurants_info[i]['Distance'] = distance_display(restaurants_info[i]["distance_float"]) # 緯度・経度から距離を計算 str
    restaurants_info = calc_recommend_score(fetch_group, group_id, restaurants_info)

    return restaurants_info


def distance_display(distance):
    '''
    距離の表示を整形します
    '''
    distance = int(distance)
    if len(str(distance)) > 3:
        distance = round(distance / 1000, 1)
        return str(distance) + "km"
    return str(distance) + "m"

    
def calc_recommend_score(fetch_group, group_id, restaurants_info):
    '''
    オススメ度を計算する
    
    Parameters
    ----------------
    restaurants_info : [dict]
    
    Returns
    ----------------
    restaurants_info : [dict]
        追加
        resul_json[i]["RecommendScore"] : float
            オススメ度をパーセントで返す
    '''
    
    # オススメ度を計算
    # 価格帯, 距離, 投票数を元に計算 
    # キープされたお店の中で、共通している条件が多いほど高スコア
    # 以下はrestaurant_idを格納
    
    try:
        group_price = fetch_group.group_price #グループの平均価格
        group_distance = fetch_group.group_distance * 1000 #グループの平均距離 m
    except:
        group_price = None
        group_distance = None
    score_list = []
    index_list = []
    for i in range(len(restaurants_info)):
        try:
            price = int(restaurants_info[i]["Price"])
            distance = restaurants_info[i]["distance_float"]
            try:
                price_score = 1 if price <= group_price else group_price / price #グループ価格に対する比でスコア付
            except:
                price_score = 0

            try:
                distance_score = 1 if distance <= group_distance else group_distance / distance #グループ距離に対する比でスコア付
            except:
                distance_score = 0

            #投票されていればスコアが計算される
            if restaurants_info[i]["VotesAll"] > 0:
                vote_score = (restaurants_info[i]["VotesLike"] / restaurants_info[i]["VotesAll"])
                score = int(round(((price_score + distance_score + vote_score) / 3) * 100, 0))
                #restaurants_info[i]["RecommendScore"] = score
                score_list.append(score)
                index_list.append(i)
            else:
                score = 0
                score_list.append(score)
                index_list.append(i)
        except:
            score_list.append(0)
            index_list.append(i)

    #normalize score
    try:
        max_score = max(score_list)
        min_score = min(score_list)
    except:
        max_score = 100
        min_score = 0
    norm_score_list = []
    M = 100 #設定したい最大値
    m = 50 #設定したい最小値
    for s in score_list:
        try:
            norm_score = ((s - min_score)*(M - m) / (max_score - min_score)) + m
        except:
            norm_score = 100 #maxとminが同じ場合は全て100
        norm_score_list.append(norm_score)
    
    for i, n_s in zip(index_list, norm_score_list):
        restaurants_info[i]["RecommendScore"] = round(n_s)

    return restaurants_info


# ============================================================================================================
# api_functions.pyで最初に呼ばれる


def create_image(restaurants_info):
    '''
    画像を繋げて1枚にする
    
    Parameters
    ----------------
    restaurants_info : [dict]
    
    Returns
    ----------------
    image : string
    '''

    images_url_list = restaurants_info['Images']
    # TODO
    image = ''
    return image