from app import config
from memory_profiler import profile
import requests, json

def test_http_info():
    url = 'http://localhost:5000/info'
    params = {
        "params":{
            "user_id": "123",
            "group_id": "456789",
            "open_hour": 12,
        }
    }
    headers = {"Content-Type":"application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    assert res


def test_http_feeling():
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
    assert res
