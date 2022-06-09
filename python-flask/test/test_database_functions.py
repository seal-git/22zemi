from app.database_functions import *
from app.internal_info import *
import pprint

def test_load_stable_restaurants_info():
    group_id = 456789
    session = database_functions.get_db_session()
    r_ids = session.query(Restaurant.id).first()
    fetch_restaurants = session.query(Restaurant).all()
    print(fetch_restaurants)
    for f in fetch_restaurants:
        print(f.id)
    r_info = load_restaurants_info(r_ids, group_id)

    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in r_info]
    assert len(r_info)==1