from app.calc_info import *

from memory_profiler import profile
@profile
def test_create_image():
    with open("test/data/references.txt", "r")as f:
        image_references = [l for l in f]
    # print(image_references)
    restaurant_info = {
        "Restaurant_id": "test",
        "Image_references": image_references,
    }
    # TODO: テスト実行のたびにお金がかかりそうなのでコメントアウト
    image_files = [True] # add_google_image(restaurant_info)
    print(image_files)
    assert image_files[0]