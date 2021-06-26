import math
def calc_recommend_score(group, restaurant_id):
    '''
    オススメ度を計算する
    
     Parameters
    ----------------
    group : dict
        current_group[group_id]
    restaurant_id : string
        レストランID
    
    Returns
    ----------------
    recommend_leve : float
        オススメ度をパーセントで返す
    '''
    
    # TODO: オススメ度を計算
    # オススメ度は全ての投票数などを格納した後の方が計算しやすい
    # 簡易版として、現状は投票数の割合
    #group = {'Coordinates': (lat,lon), 
    # 'Users': { 'user_id1: {'RequestCount': 0, 'Feeling': {restaurant_id1: true, ... }, 
    # 'UnanimousNoticed': [restaurant_id1, ... ]}, ... }, 'Unanimous': [restaurant_id1, ... ]}, ... }
    votes_like, votes_all = count_votes(group, restaurant_id)
    users_num = len(group['Users'].values())
    try:
        score = round((votes_like / votes_all) * 100, 1)
    except:
        score = 0
    return score

def count_votes(group, restaurant_id):
    # 投票数を数える
    if restaurant_id in group['Restaurants']:
        return len(group['Restaurants'][restaurant_id]['Like']), len(group['Restaurants'][restaurant_id]['All'])
    else:
        return 0, 0
