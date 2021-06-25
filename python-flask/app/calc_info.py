def recommend_level(group, restaurant_id):
    '''
    オススメ度を計算してパーセントで返す
    '''
    # TODO: オススメ度を計算
    return 100.0

def count_votes(group, restaurant_id):
    # 投票数を数える
    votes_like = 0
    votes_all = 0
    for u in group['Users'].values():
        if restaurant_id in u['Feeling']:
            votes_all += 1
            if u['Feeling'][restaurant_id]: 
                votes_like += 1
    return votes_like, votes_all
