from app.call_api import *
from app.internal_info import *
from app import database_functions
import pprint

def test_search_restaurants_info():
    user_id = 123
    group_id = 456789
    place = "新宿駅"
    recommend_method = config.MyConfig.RECOMMEND_METHOD
    api_method = "yahoo"
    database_functions.register_user_and_group_if_not_exist(group_id,
                                                            user_id,
                                                            place,
                                                            recommend_method,
                                                            api_method
                                                            )
    fetch_group = session.query(Group).filter(Group.id==group_id).first()
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
    group_id = 456789
    fetch_group = session.query(Group).filter(Group.id==group_id).first()
    r_id = session.query(Restaurant.id).first()
    restaurants_info = database_functions.load_restaurants_info(r_id)
    restaurants_info = get_restaurants_info(fetch_group,
                                            group_id,
                                            restaurants_info)
    [pprint.PrettyPrinter(indent=2).pprint(r.get_dict()) for r in restaurants_info]
    assert len(restaurants_info)>0

