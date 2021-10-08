from app import config
from memory_profiler import profile
import time
import requests, json, pprint

def test_http_info():
    url = 'http://localhost:5000/info'
    params = {
        "params":{
            "user_id": "123",
            "group_id": "456789",
            "open_hour_str": "12:00",
        }
    }
    headers = {"Content-Type":"application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    pprint.PrettyPrinter(indent=2).pprint(res.json())

    assert res


def test_http_feeling():
    time.sleep(1)
    url = 'http://localhost:5000/feeling'
    params = {
        "params":{
            "user_id": "123",
            "restaurant_id": "5ce1ffb50b7c586e52e37235d076fd7ba6e647d4",
            "feeling": True,
        }
    }
    headers = {"Content-Type":"application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    pprint.PrettyPrinter(indent=2).pprint(res.json())

    assert res
