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
        
    for i in range(len(result_json)):
        try:
            for p in price_list:
                    if i in p:
                        price_score = (len(p) / len(result_json))
            for d in distance_list:
                if i in d:
                    distance_score = (len(d) / len(result_json))

            if result_json[i]["VotesAll"] > 1:
                vote_score = (result_json[i]["VoteLike"] / result_json[i]["VoteAll"])
                score = round(((price_score + distance_score + vote_score) / 3) * 100, 1)
                result_json[i]["RecommendScore"] = score
            else:
                score = round(((price_score + distance_score) / 2) * 100, 1)
                result_json[i]["RecommendScore"] = score
        except:
            result_json[i]["RecommendScore"] = -1

    return result_json

def count_votes(group, restaurant_id):
    # 投票数を数える
    if restaurant_id in group['Restaurants']:
        return len(group['Restaurants'][restaurant_id]['Like']), len(group['Restaurants'][restaurant_id]['All'])
    else:
        return 0, 0
