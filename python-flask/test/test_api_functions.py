from app.api_functions import *
from app.internal_info import *
import datetime

def test_yahoo_local_search_with_param():
    params = Params()
    params.query = ""
    params.lat = 35.68242136685908
    params.lon = 139.73671070104604
    params.max_dist = 20000
    params.image = True
    restaurants_info = yahoo_local_search(params=params)
    print("yahoo_local_search_with_param")
    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in restaurants_info]
    assert len(restaurants_info)>0

def test_yahoo_local_search_with_param_2():
    params = Params()
    params.query = "和食"
    params.lat = 35.0101165
    params.lon = 135.7514639
    params.open_day = datetime.datetime.now().day
    params.open_hour = 12
    params.results = 10
    params.max_price = 2000
    # params.image = True
    restaurants_info = yahoo_local_search(params=params)
    print("yahoo_local_search_with_param_2")
    [pprint.PrettyPrinter(indent=2).pprint(r.get_dict()) for r in restaurants_info]
    assert len(restaurants_info)>0

def test_yahoo_local_search_with_id():
    r_info = RestaurantInfo()
    r_info.yahoo_id = "5ce1ffb50b7c586e52e37235d076fd7ba6e647d4"
    r_info = yahoo_local_search(r_info=r_info)
    print("yahoo_local_search_with_id")
    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in r_info]
    assert len(r_info)==1

def test_yahoo_contents_geocoder():
    place = "東京ガーデンテラス紀尾井町 紀尾井タワー"
    lat, lon, address = yahoo_contents_geocoder(place)
    print(f"lat:{lat} lon:{lon} address:{address}")



"""
def test_google_find_place():
    r_info = RestaurantInfo()
    r_info.id = "5ce1ffb50b7c586e52e37235d076fd7ba6e647d4"
    r_info.name = "ザ・ロビー/ザ・ペニンシュラ東京"
    r_info = google_find_place(r_info)
    assert r_info.google_id is not None

def test_google_place_details():
    r_info = RestaurantInfo()
    r_info.google_id = "ChIJ55FqKPCLGGAR2GqcmoYJNzM"
    r_info.name = "ザ・ロビー/ザ・ペニンシュラ東京"
    r_info = google_place_details(r_info)
    pprint.PrettyPrinter(indent=2).pprint(r_info.get_dict())
    assert len(r_info.google_photo_reference) > 0
<<<<<<< HEAD

def test_google_place_photo():
    photo_reference = 'Aap_uEDbtTwOXOryFJYq3129RPKnlC4JRe4XVjFWnqb3uT2aGsCHUdOW9_TetRCnFkaSnd3dWgrqfzjJYDUX1s5DK6blbKeZ780kfTV-t546Er998J5Wr1ddhaNwmZ9CvCivrKNllfzREoU1mqxcgqYvtUxsRAWAwHQDqh_Uw3DuPEv10U8m'
    image_width = 400
    image = google_place_photo(photo_reference, image_width)

    assert image
=======
"""

>>>>>>> 01871bb0d1ae7b4dc1870d410a9dbf006811828a
