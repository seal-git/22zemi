from app.database_functions import *
from app.internal_info import *
import pprint

def test_load_stable_restaurants_info():
    group_id = 456789
    session = database_functions.get_db_session()
    r_ids = session.query(Restaurant.id).first()

    # database_functions.save_votes()の処理。Votesにレコードを挿入する
    for i,r in enumerate(r_ids):
        if r is None: continue
        fetch_vote = session.query(Vote).filter(
            Vote.group == group_id, Vote.restaurant == r
                                ).with_for_update().first()
        if fetch_vote is None:
            fetch_vote = Vote()
            fetch_vote.group = group_id
            fetch_vote.restaurant = r
        fetch_vote.votes_like = 0
        fetch_vote.votes_all = 0
        fetch_vote.number_of_participants = 1
        fetch_vote.recommend_priority = 1
        fetch_vote.price = 1000
        fetch_vote.opening_hours = 18
        fetch_vote.distance_float = 0.5
        fetch_vote.distance_str = "500m"
        fetch_vote.recommend_score = 1
        session.add(fetch_vote)
        session.commit()
    session.close()

    fetch_restaurants = session.query(Restaurant).all()
    print(fetch_restaurants)
    for f in fetch_restaurants:
        print(f.id)
    r_info = load_restaurants_info(r_ids, group_id)

    [pprint.PrettyPrinter(indent=2).pprint(r.name) for r in r_info]
    assert len(r_info)==1