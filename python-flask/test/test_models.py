from app import config
from memory_profiler import profile
import time
import requests, json, pprint


def _test_http_info_1():
    url = 'http://localhost:5000/info'
    params = {
        "params": {
            "user_id": "123",
            "group_id": "456789",
            "open_hour_str": "12:00",
        }
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    pprint.PrettyPrinter(indent=2).pprint(res.json())

    assert res


def _test_http_info_2():
    url = 'http://localhost:5000/info'
    params = {
        "params": {
            'user_id': '203326',
            'group_id': '399207',
            'genre': '',
            'maxprice': '4000',
            'open_hour': 0,
            'open_hour_str': '',
            'place': '',
        }
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    pprint.PrettyPrinter(indent=2).pprint(res.json())

    assert res


def _test_http_feeling():
    time.sleep(1)
    url = 'http://localhost:5000/feeling'
    params = {
        "params": {
            "user_id": "123",
            "restaurant_id": "5ce1ffb50b7c586e52e37235d076fd7ba6e647d4",
            "feeling": True,
        }
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    pprint.PrettyPrinter(indent=2).pprint(res.json())

    assert res

def test_http_invite():
    url = 'http://localhost:5000/invite'
    params = {
        "params": {
            'user_id': '203326',
            'group_id': '399207',
            'genre': '',
            'maxprice': '4000',
            'open_hour': 0,
            'place': '',

        }
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    pprint.PrettyPrinter(indent=2).pprint(res.json())

    assert res
