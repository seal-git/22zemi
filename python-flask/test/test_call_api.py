from app.call_api import *
from app.internal_info import *
from app import database_functions
import pprint

def test_search_restaurants_info():
    user_id = 123
    group_id = 456789
    fetch_group = session.query(Group).one()
    api = "yahoo_local_search"

    params = Params()
    params.query = ""
    params.lat = 35.68242136685908
    params.lon = 139.73671070104604
    params.dist = 20000
    params.image = True
    restaurants_info = search_restaurants_info(fetch_group,
                                               group_id,
                                               user_id,
                                               params,
                                               api)

    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in restaurants_info]
    assert len(restaurants_info)>0

def test_get_restaurants_info():
    fetch_group = session.query(Group).one()
    group_id = 456789
    r_id = ["5ce1ffb50b7c586e52e37235d076fd7ba6e647d4"]
    restaurants_info = database_functions.load_stable_restaurants_info(r_id)
    restaurants_info = get_restaurants_info(fetch_group,
                                            group_id,
                                            restaurants_info)
    assert len(restaurants_info)>0

