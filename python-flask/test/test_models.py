from app.models import *
from memory_profiler import profile

def test_http_info():
    url = 'http://localhost:5000/info'
    params = {
        "params":{
            "user_id": "123",
            "group_id": "456789",
        }
    }
    headers = {"Content-Type":"application/json"}
    res = requests.post(url=url, data=json.dumps(params), headers=headers)
    assert res
