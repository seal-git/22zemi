def hello():
    print('hello')
    return 0

def test_hello():
    res = hello()
    assert res==0