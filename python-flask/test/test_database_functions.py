from app.database_functions import *
from app.internal_info import *
import pprint

def test_load_stable_restaurants_info():
    r_ids = ["5ce1ffb50b7c586e52e37235d076fd7ba6e647d4"]
    fetch_restaurants = session.query(Restaurant).all()
    print(fetch_restaurants)
    for f in fetch_restaurants:
        print(f.id)
    r_info = load_stable_restaurants_info(r_ids)

    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in r_info]
    assert len(r_info)==1