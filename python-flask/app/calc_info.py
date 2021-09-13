import os

from geopy.distance import great_circle
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
import requests

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
        price_average = fetch_group.price_average #グループの平均価格
        distance_average = fetch_group.distance_average #グループの平均距離 m
    except:
        price_average = None
        distance_average = None
    score_list = []
    index_list = []
    for i in range(len(restaurants_info)):
        try:
            price = int(restaurants_info[i]["Price"])
            distance = restaurants_info[i]["distance_float"]
            try:
                price_score = 1 if price <= price_average else price_average / price #グループ価格に対する比でスコア付
            except:
                price_score = 0

            try:
                distance_score = 1 if distance <= distance_average else distance_average / distance #グループ距離に対する比でスコア付
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

    if len(score_list) == 0:
        for i,r in enumerate(restaurants_info):
            restaurants_info[i]["RecommendScore"] = 100

    #normalize score
    max_score = max(score_list) if len(score_list) != 0 else 100
    min_score = min(score_list) if len(score_list) != 0 else 100
    norm_score_list = []
    M = 100 #設定したい最大値
    m = 50 #設定したい最小値
    for s in score_list:
        if (max_score != min_score):
            norm_score = ((s - min_score)*(M - m) / (max_score - min_score)) + m
        else:
            norm_score = 100 #maxとminが同じ場合は全て100
        norm_score_list.append(norm_score)
    
    for i, n_s in zip(index_list, norm_score_list):
        restaurants_info[i]["RecommendScore"] = round(n_s)

    return restaurants_info


# ============================================================================================================
# api_functions.pyで最初に呼ばれる

def get_google_images(restaurant_name):
    if not os.environ["USE_LOCAL_IMAGE"]: # debug mode
        print("getting image reference from test/data")
        with open("test/data/references.txt", "r")as f:
            image_references = [l for l in f]
        return image_references
    else:
        # place検索
        url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
        params = {
            'key': os.environ["GOOGLE_API_KEY"],
            'input': restaurant_name,
            'inputtype': 'textquery',
        }
        res = requests.get(url=url, params=params)
        dic = res.json()
        place_id = dic['candidates'][0]['place_id']

        # place_detailを取得
        url = 'https://maps.googleapis.com/maps/api/place/details/json'
        params = {
            'key': os.environ["GOOGLE_API_KEY"],
            'place_id': place_id,
        }
        res = requests.get(url=url, params=params)
        dic = res.json()
        if 'photos' in dic['result']:
            photo_references = [photo['photo_reference'] for photo in dic['result']['photos']]
        else:
            photo_references = []
    return photo_references

def create_image(restaurant_info, debug=True):
    '''
    画像をGoogleAPIから読み込んで、つなぎ合わせる。
    縦2列に並んだ画像が800x1200の1枚の画像になる。
    生成された画像はbase64でエンコードされる。
    画像ファイル名は、「restaurantID_」+通し番号で、data/imageに保存される。
    確認用に実際のjpg画像を保存することもできる。コメントアウトして使用。
    デバッグ中は余計なAPIを呼ばないようにtest/dataの画像を呼び出す。環境変数のUSE_APIをTrueすると実際のAPIを呼び出せる。

    Parameters
    ----------------
    restaurant_info : [dict]
    debug : bool : デバッグ中はAPIを呼び出さないようにtest/data/から画像を読み込む。
    
    Returns
    ----------------
    image_files : [string] base64でエンコードしたバイナリファイルのファイル名のリスト
    '''
    from PIL import Image
    import os
    import requests
    from io import BytesIO
    import base64

    debug = os.getenv("USE_LOCAL_IMAGE")

    image_references = restaurant_info['Image_references']
    url = 'https://maps.googleapis.com/maps/api/place/photo'
    image_width = 400 #画像1枚の最大幅
    images = [] # お店の写真のImageオブジェクトのリスト
    height_sum = 0
    # image_referenceごとに画像を取得
    for i, reference in enumerate(image_references):
        # APIを叩く
        params = {
            'key': os.environ['GOOGLE_API_KEY'],
            'photoreference': reference,
            'maxwidth': image_width,
        }
        if debug: # debug mode
            print("create_image: getting test data")
            _image = Image.open(f"test/data/image{i}.jpg")
        else:
            # image_referenceごとにAPIを叩いて画像を取得
            res = requests.get(url=url, params=params)
            # 返ってきたバイナリをImageオブジェクトに変換
            _image = Image.open(BytesIO(res.content))

        images.append(_image)
        height_sum += _image.height

    # 1行に入る画像のインデックスを計算する
    rows = []
    rows.append([])
    _row_count = 0
    _height = 0
    for i, _image in enumerate(images):
        if _height+_image.height < 1200:
            rows[_row_count].append(i)
            _height += _image.height + 10
        else:
            rows.append([i,])
            _height = _image.height
            _row_count += 1
    if len(rows)%2!=0: #rowsは偶数になるようにする
        rows.append([])
    print(rows)

    # 2行ごとに画像生成し、リサイズしてつなぎ合わせて保存
    image_files = []
    for idx in range(int(len(rows)/2)):
        # 1行目の生成
        row1_image = Image.new("RGB", (400,1200))
        _height = 0
        for i in rows[idx*2]:
            row1_image.paste(images[i], (0,_height))
            _height += images[i].height + 10
        row1_image = row1_image.crop((0,0,400,max(1,_height-10)))
        # 2行目の生成
        row2_image = Image.new("RGB", (400,1200))
        _height = 0
        for i in rows[idx*2+1]:
            row2_image.paste(images[i], (0,_height))
            _height += images[i].height + 10
        row2_image = row2_image.crop((0,0,400,max(1,_height-10)))
        # 2行目をリサイズして1行目の高さに合わせる
        row2_image = row2_image.resize(
            (int(row2_image.width*row1_image.height/row2_image.height),
            row1_image.height)
        )
        # 1行目と2行目をつなぎ合わせてリサイズする
        row12_image = Image.new(
            "RGB",
            (row1_image.width+row2_image.width+10,
            row1_image.height)
        )
        row12_image.paste(row1_image,(0,0))
        row12_image.paste(row2_image, (row1_image.width+10, 0))
        row12_image = row12_image.resize(
            (800,
            max(1,int(row12_image.height*800/row12_image.width)))
        )
        # new_imageにつなぎ合わせる
        new_image = Image.new("RGB", (800, 1200))
        new_image.paste(row12_image, (0, 0))

        # データの保存
        filename = restaurant_info['Restaurant_id']+"_"+str(idx)
        buffer = BytesIO()
        new_image.save(buffer, format="jpeg")
        new_image_str = base64.b64encode(buffer.getvalue()).decode("ascii")
        with open(f"./data/image/{filename}", "w") as f:
            f.write(new_image_str)
        if debug:
            new_image.save(f"./data/tmp/{filename}.jpg")
        else:
            new_image.save(f"./data/tmp/{filename}.jpg")
        image_files.append(filename)

    return image_files
