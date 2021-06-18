import requests
import json
import os

def get_lat_lon(query):
    '''
    緯度，経度をfloatで返す関数
    example：
    input：query = "千代田区"
    output：lat = 35.69404120, lon = 139.75358630
    '''
    print(os.getenv('YAHOO_LOCAL_SEARCH_API_CLIENT_ID'))
    geo_coder_url = "https://map.yahooapis.jp/geocode/cont/V1/contentsGeoCoder"
    params = {
        "appid": os.environ['YAHOO_LOCAL_SEARCH_API_CLIENT_ID'],
        "output": "json",
        "query": query
    }
    response = requests.get(geo_coder_url, params=params)
    response = response.json()
    geometry = response["Feature"][0]["Geometry"]
    coordinates = geometry["Coordinates"].split(",")
    lon = float(coordinates[0])
    lat = float(coordinates[1])
    return lat, lon