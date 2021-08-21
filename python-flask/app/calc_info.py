import math
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History


def save_restaurants_info(restaurants_info):
    for restaurant_info in restaurants_info:
        fetch_restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_info['Restaurant_id']).first()
        if fetch_restaurant is None:
            new_restaurant = Restaurant()
            new_restaurant.id = restaurant_info['Restaurant_id']
            new_restaurant.name = restaurant_info['Name']
            new_restaurant.address = restaurant_info['Address']
            new_restaurant.distance_float = restaurant_info.get('DistanceFloat')
            new_restaurant.distance = restaurant_info.get('Distance')
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
            new_restaurant.menu = restaurant_info.get('Menu')
            session.add(new_restaurant)
            session.commit()


def load_restaurants_info(self_class, fetch_group, group_id, restaurant_ids):

    restaurants_info = [None for rid in restaurant_ids]
    fetch_restaurants = session.query(Restaurant).filter(Restaurant.id.in_(restaurant_ids)).all()
    for f_restaurant in fetch_restaurants:
        restaurant_info = {}
        restaurant_info['Restaurant_id'] = f_restaurant.id
        restaurant_info['Name'] = f_restaurant.name
        restaurant_info['Address'] = f_restaurant.address
        restaurant_info['DistanceFloat'] = f_restaurant.distance_float
        restaurant_info['Distance'] = f_restaurant.distance
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
        restaurant_info['Menu'] = f_restaurant.menu

        restaurants_info[ restaurant_ids.index(f_restaurant.id) ] = restaurant_info

    rest_ids = [rid for rid, r_info in zip(restaurant_ids, restaurants_info) if r_info is None]
    rs_info = self_class.get_restaurants_info(fetch_group, group_id, rest_ids)
    for r_info in rs_info:
        restaurants_info[ restaurant_ids.index(r_info['Restaurant_id']) ] = r_info
        

def distance_display(distance):
    '''
    距離の表示を整形します
    '''
    distance = int(distance)
    if len(str(distance)) > 3:
        distance = round(distance / 1000, 1)
        return str(distance) + "km"
    return str(distance) + "m"

    
def calc_recommend_score(fetch_group, group_id, result_json):
    '''
    オススメ度を計算する
    
    Parameters
    ----------------
    result_json : dict
    
    Returns
    ----------------
    result_json : dict
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
    for i in range(len(result_json)):
        try:
            price = int(result_json[i]["Price"])
            distance = result_json[i]["distance_float"]
            try:
                price_score = 1 if price <= group_price else group_price / price #グループ価格に対する比でスコア付
            except:
                price_score = 0

            try:
                distance_score = 1 if distance <= group_distance else group_distance / distance #グループ距離に対する比でスコア付
            except:
                distance_score = 0

            #投票されていればスコアが計算される
            if result_json[i]["VotesAll"] > 0:
                vote_score = (result_json[i]["VotesLike"] / result_json[i]["VotesAll"])
                score = int(round(((price_score + distance_score + vote_score) / 3) * 100, 0))
                #result_json[i]["RecommendScore"] = score
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
    max_score = max(score_list)
    min_score = min(score_list)
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
        result_json[i]["RecommendScore"] = round(n_s)

    return result_json
