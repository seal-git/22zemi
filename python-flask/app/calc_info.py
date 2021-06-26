def recommend_level(group, restaurant_id):
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
    return 100.0

def count_votes(group, restaurant_id):
    # 投票数を数える
    if restaurant_id in group['Restaurants']:
        return len(group['Restaurants'][restaurant_id]['Like']), len(group['Restaurants'][restaurant_id]['All'])
    else:
        return 0, 0
