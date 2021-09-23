from app.api_functions import *
from app.internal_info import *

def test_yahoo_local_search_with_param():
    params = Params()
    params.query = ""
    params.lat = 35.68242136685908
    params.lon = 139.73671070104604
    params.dist = 20000
    params.image = True
    restaurants_info = yahoo_local_search(params=params)
    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in restaurants_info]
    assert len(restaurants_info)>0

def test_yahoo_local_search_with_id():
    r_info = RestaurantInfo()
    r_info.yahoo_id = "5ce1ffb50b7c586e52e37235d076fd7ba6e647d4"
    r_info = yahoo_local_search(r_info=r_info)
    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in r_info]
    assert len(r_info)==1