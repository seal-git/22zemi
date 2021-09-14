from app.calc_info import *

from memory_profiler import profile
@profile
def test_create_image():
    with open("test/data/references.txt", "r")as f:
        image_references = [l for l in f]
    # print(image_references)
    restaurants_info = {
        "Restaurant_id": "test",
        "Image_references": image_references,
    }
    image_files = create_image(restaurants_info)
    print(image_files)
    assert image_files[0]