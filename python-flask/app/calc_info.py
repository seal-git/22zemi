import math
    
def calc_recommend_score(result_json):
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
    # 個人かグループ化で式を区別
    # 以下はrestaurant_idを格納
    price_list = [[],[],[],[],[]] #~1500円, 1500~3000円, 3000~5000, 5000~10000, 10000~
    distance_list = [[],[],[],[]] #~500m, 500~1000m, 1000~2000, 2000~
    for i in range(len(result_json)):
        try:
            price = int(result_json[i]["Price"])
            distance = result_json[i]["distance_float"]
            if price < 1500:
                price_list[0].append(i)
            elif 1500 >= price < 3000:
                price_list[1].append(i)
            elif 3000 >= price < 5000:
                price_list[2].append(i)
            elif 5000 >= price < 10000:
                price_list[3].append(i)
            elif price >= 10000:
                price_list[4].append(i)
            
            if distance < 500:
                distance_list[0].append(i)
            elif 500 >= distance < 1000:
                distance_list[1].append(i)
            elif 1000 >= distance < 2000:
                distance_list[2].append(i)
            elif distance >= 2000:
                distance_list[3].append(i)
        except:
            continue
        
    score_list = []
    index_list = []
    for i in range(len(result_json)):
        try:
            for p in price_list:
                if i in p:
                    try:
                        price_score = (len(p) / len(result_json))
                    except:
                        price_score = 0
            for d in distance_list:
                if i in d:
                    try:
                        distance_score = (len(d) / len(result_json))
                    except:
                        distance_score = 0

            if result_json[i]["VotesAll"] > 1:
                vote_score = (result_json[i]["VoteLike"] / result_json[i]["VoteAll"])
                score = int(round(((price_score + distance_score + vote_score) / 3) * 100, 0))
                #result_json[i]["RecommendScore"] = score
                score_list.append(score)
                index_list.append(i)
            else:
                score = int(round(((price_score + distance_score) / 2) * 100, 0))
                #result_json[i]["RecommendScore"] = score
                score_list.append(score)
                index_list.append(i)
        except:
            score_list.append(0)
            index_list.append(i)
            #result_json[i]["RecommendScore"] = 0
    
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

def count_votes(group, restaurant_id):
    # 投票数を数える
    if restaurant_id in group['Restaurants']:
        return len(group['Restaurants'][restaurant_id]['Like']), len(group['Restaurants'][restaurant_id]['All'])
    else:
        return 0, 0
