import glob
import os

from geopy.distance import great_circle
from app import database_functions, api_functions
from app.database_setting import * # session, Base, ENGINE, User, Group, Restaurant, Belong, History, Vote
import requests
import datetime

'''

api_functionsで使う情報を計算する

'''


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
        restaurants_info[i].votes_like = session.query(History).filter(History.group==group_id,
                                                                    History.restaurant==restaurants_info[i].id,
                                                                    History.feeling==True
                                                                    ).count() # レストランのいいね数
        restaurants_info[i].votes_all = session.query(History).filter(History.group==group_id,
                                                                      History.restaurant==restaurants_info[i].id,
                                                                      History.feeling is not None
                                                                      ).count() # レストランの投票人数
        restaurants_info[i].number_of_participants = str(database_functions.get_participants_count(group_id)) # グループの参加人数
        restaurants_info[i].distance_float = great_circle((fetch_group.lat, fetch_group.lon),
                                                          (restaurants_info[i].lat, restaurants_info[i].lon)
                                                          ).m #距離 メートル float
        restaurants_info[i].distance = distance_display(restaurants_info[i].distance_float) # 緯度・経度から距離を計算 str

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
            price = int(restaurants_info[i].price)
            distance = restaurants_info[i].distance_float
            try:
                price_score = 1 if price <= price_average else price_average / price #グループ価格に対する比でスコア付
            except:
                price_score = 0

            try:
                distance_score = 1 if distance <= distance_average else distance_average / distance #グループ距離に対する比でスコア付
            except:
                distance_score = 0

            #投票されていればスコアが計算される
            if restaurants_info[i].votes_all > 0:
                vote_score = (restaurants_info[i].votes_like / restaurants_info[i].votes_all)
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
            restaurants_info[i].recommend_score = 100

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
        restaurants_info[i].recommend_score = round(n_s)

    return restaurants_info


def add_price(fetch_group, group_id, restaurants_info):
    if fetch_group.open_hour:
        hour = int(fetch_group.open_hour.hour)
    else:
        hour = datetime.datetime.now().hour + datetime.datetime.now().minute / 60

    for i in range(len(restaurants_info)):
        if config.MyConfig.LUNCH_TIME_START <= hour < config.MyConfig.LUNCH_TIME_END:
            restaurants_info[i].price = restaurants_info[i].lunch_price
        else:
            restaurants_info.price = restaurants_info.dinner_price

    return restaurants_info



# calc_info行き
def get_review_rating(restaurant_info):
    '''
    Yahoo APIにアクセスして口コミを文字列で返す
    '''
    review_rating_int = int(review_rating + 0.5)
    review_rating_star = '★' * review_rating_int + '☆' * (5-review_rating_int)

    restaurant_info.rating = review_rating_star + '    ' + ('%.1f' % review_rating)

    return restaurant_info

def get_google_images(restaurant_name):
    if os.getenv("USE_LOCAL_IMAGE")=="True": # debug mode
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

from memory_profiler import profile
@profile
def create_image(restaurant_info):
    '''
    画像をGoogleAPIから読み込んで、つなぎ合わせる。
    縦2列に並んだ画像が800x1200の1枚の画像になる。
    生成された画像はbase64でエンコードされる。
    画像ファイル名は、「restaurantID_」+通し番号で、data/imageに保存される。
    確認用に実際のjpg画像を保存することもできる。コメントアウトして使用。
    環境変数のUSE_LOCAL_APIをTrueにすると画像をtest/dataからとってくる。
    環境変数のUSE_RAW_IMAGEをTrueにすると画像を結合せずそのままb64で保存する。

    Parameters
    ----------------
    restaurant_info : [dict]

    Returns
    ----------------
    image_files : [string] base64でエンコードしたバイナリファイルのファイル名のリスト
    '''
    from PIL import Image
    import os, sys, requests, base64, gc
    from io import BytesIO

    # imageをそのまま扱うとメモリリークするので、サイズとファイル名の構造体として扱う
    class ImageInfo:
        def __init__(self, filename=None, width=None, height=None):
            self.filename = filename
            self.width = width
            self.height = height
    
    def save_b64(filename, image):
        buffer = BytesIO()
        image.save(buffer, format="jpeg")
        with open(filename, "w") as f:
            f.write(base64.b64encode(buffer.getvalue()).decode("ascii")
)
        del buffer, image
        gc.collect()

    use_local_image = os.getenv("USE_LOCAL_IMAGE")=="True"
    use_raw_image = os.getenv("USE_RAW_IMAGE")=="True"
    if use_local_image:
        print("create_image: getting test data")
    if use_raw_image:
        print("create_image: return raw image: not create one image")

    image_references = restaurant_info['Image_references']
    url = 'https://maps.googleapis.com/maps/api/place/photo'
    image_width = 400 #画像1枚の最大幅
    image_info_list = [] # お店の写真のfilename, width, heightのリスト
    image_file_list = [] # 画像のb64のパスのリスト
    height_sum = 0
    # image_referenceごとに画像を取得
    for i, reference in enumerate(image_references):
        # APIを叩く
        params = {
            'key': os.environ['GOOGLE_API_KEY'],
            'photoreference': reference,
            'maxwidth': image_width,
        }
        filename = restaurant_info['Restaurant_id'] + "_" + str(i)

        if use_local_image: # debug mode
            _image = Image.open(f"test/data/image{i}.jpg")
            _image.save(f"data/tmp/image{i}.jpg")
        else:
            # image_referenceごとにAPIを叩いて画像を取得
            res = requests.get(url=url, params=params)
            # 返ってきたバイナリをImageオブジェクトに変換
            _image = Image.open(BytesIO(res.content))
            _image.save(f"data/tmp/image{i}.jpg")

        _image_info = ImageInfo(
            filename = f"data/tmp/image{i}.jpg",
            width = _image.width,
            height = _image.height
        )
        image_info_list.append(_image_info)
        height_sum += _image.height
        print(f"_image{i}", sys.getsizeof(_image.tobytes()))

        if use_raw_image:
            save_b64(f"data/image/{filename}", _image)
            image_file_list.append(f"{filename}")

    if use_raw_image:
        return image_file_list

    # 1行に入る画像のインデックスを計算する
    rows = []
    rows.append([])
    _row_count = 0
    _height = 0
    for i, _image in enumerate(image_info_list):
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
    image_file_list = []
    for idx in range(len(rows)//2):
        # 1行目の生成
        row1_image = Image.new("RGB", (400, 1200), "#ffffff")
        _height = 0
        for i in rows[idx*2]:
            row1_image.paste(Image.open(image_info_list[i].filename), (0,_height))
            _height += image_info_list[i].height + 10
        row1_image = row1_image.crop((0,0,400,max(1,_height-10)))
        # 2行目の生成
        _height = 0
        row2_image = Image.new("RGB", (400, 1200), "#ffffff")
        for i in rows[idx*2+1]:
            row2_image.paste(Image.open(image_info_list[i].filename), (0,_height))
            _height += image_info_list[i].height + 10
        row2_image = row2_image.crop((0,0,400,max(1,_height-10)))
        # 2行目をリサイズして1行目の高さに合わせる
        row2_image = row2_image.resize(
            (row2_image.width*row1_image.height//row2_image.height,
            row1_image.height)
        )
        print(f"row_image{idx}", sys.getsizeof(row1_image.tobytes()))
        print(f"row1_image{idx}", sys.getsizeof(row2_image.tobytes()))
        # 1行目と2行目をつなぎ合わせてリサイズする
        row12_image = Image.new(
            "RGB",
            (row1_image.width+row2_image.width+10,
            row1_image.height),
            "#ffffff"
        )
        row12_image.paste(row1_image,(0,0))
        row12_image.paste(row2_image, (row1_image.width+10, 0))
        row12_image = row12_image.resize(
            (800,
            max(1,row12_image.height*800//row12_image.width))
        )
        # new_imageにつなぎ合わせる
        new_image = Image.new("RGB", (800, 1200))
        new_image.paste(row12_image, (0, 0))

        # 画像のb64の保存
        filename = restaurant_info['Restaurant_id']+"_"+str(idx)
        save_b64(f"data/image/{filename}", new_image)
        image_file_list.append(filename)
        print(f"create_image: file saved at data/image/{filename}")
        # 画像の保存
        if use_local_image:
            new_image.save(f"./data/tmp/{filename}.jpg")
        else:
            new_image.save(f"./data/tmp/{filename}.jpg")
        print(f"new_image{idx}", sys.getsizeof(new_image.tobytes()))

        # メモリ解放
        # del row12_image
        # gc.collect()


    # メモリ解放
    del row1_image, row2_image, row12_image, new_image
    gc.collect()
    # キャッシュファイル削除
    [os.remove(file) for file in glob.glob("data/tmp/image*.jpg")]


    return image_file_list

