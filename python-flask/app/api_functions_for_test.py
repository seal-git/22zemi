import requests
import datetime
from app import config
from app.internal_info import *
from flask import abort
import pprint
import re
import time
from PIL import Image
import os, requests
from io import BytesIO

"""
無駄にapiを叩かないための偽api
"""


def google_find_place(r_info):
    """
    google find placeでお店のgoogle_idを取得
    Parameters
    ----------
    r_info

    Returns
    -------
    r_info
    """
    # place検索
    print(f"find place: {r_info.name}")
    res = {
        'place_id': "ChIJ55FqKPCLGGAR2GqcmoYJNzM"
    }
    time.sleep(0.1)

    if r_info.id is None: r_info.id = res['place_id']
    r_info.google_id = res['place_id']

    return r_info


def google_place_details(r_info: RestaurantInfo):
    """
    place_detailを取得

    Parameters
    ----------
    r_info

    Returns
    -------

    """
    print(f"place details: {r_info.name}")

    res = {
        "photos": [
            {"photo_reference": 'Aap_uEDbtTwOXOryFJYq3129RPKnlC4JRe4XVjFWnqb3uT2aGsCHUdOW9_TetRCnFkaSnd3dWgrqfzjJYDUX1s5DK6blbKeZ780kfTV-t546Er998J5Wr1ddhaNwmZ9CvCivrKNllfzREoU1mqxcgqYvtUxsRAWAwHQDqh_Uw3DuPEv10U8m'},
            {"photo_reference": 'Aap_uECsaUYAWmWcfVg-wfOiiZrjpC9pG1ltHJWjNYM6ZUJcZUmSSZPncqkxr3KjBw7tda-MSkh5LJ9hywUCTPwA1mgOEJgC-vPdvnrlDq8cq_605erDwvUFD-50c6t37ZY37H-xDziFz0hsfv45k-t6GPB6L30fCpGTfRkZTd8FciQZO2sZ'},
            {"photo_reference": 'Aap_uEDgr8xIfyH_aEui85bN-L0K-DXuAg_uU9yptSzdW5QF_4V4ZTsbbt-PO2AnMbEXPCNMqCh7-WEsx-nYwVbRPDuAeHHwVQpBbmHbS5mKK1fRQP0IXElOCLckGdyUAUgT4Uba4WIoqFtf3ov5kj0P7f57Py8xSsIOXBdvQCWI-sAcNmuF'},
            {"photo_reference": 'Aap_uEAntKCd9lpMdWIuqK48qOt_-lWAEvqA1Z_lox3GLgQDoABzpyTiof_R-s-eZaEGDTN1ecNLOGMbtLBQfdoRAKbi94vkx5Wm8gzhYXy6_EEtj3uR1eKm_DXI96SOx1XZ8gFiPvVGTMfU4oVGM06NY8sftxLZNcWY6jKdkR6x8VDZ5CSa'},
            {"photo_reference": 'Aap_uEBUKfR9lc0sZH-8voZQCaSaI2PH-nfhoyk5qAfX_edP_iztMZptI3u-mnm70kF00QmtLjMl63GBFLbQaXytJ9_ttQn9EX1Weobt1RXxiDhLIoKNuCOiqZ6mtxB_ue1h5_DAMzztwkG04uIYs0fbkOFw3qd2oHBdeuFCqe5zyTklRV4s'},
            {"photo_reference": 'Aap_uEBEZ_Iul32mxYV03G-kya_FQD8kTRXdM9vIh3a0wjSS03e_O28pifepAWTrtLSZcD27-qtJ-pGDzb6K7hSkB7wnRCBVeofz9LbH5vQTID9fBhJrQYeamiUjzbwwtjc6opbv452eTfXde4V-ZVSqeQabh4lFL3c9_KMlPDrVHGrTUi_k'},
            {"photo_reference": 'Aap_uEDsAHVfe726OdmnK6y_CMCGhmmGt2JxQzN6YXyGbhEmIZopgLFeDakTFE6JdlHQrduVhxEUQVjC1_uRxFaO5JGKoIjb6JSit67ybtJnH4zQHJfRGIK5Ia-jJGbpEoDG0H6VfelS2Y50_J_J7EAdvBZ-qDnVfujsRNzNx3lo_rVTsES8'},
            {"photo_reference": 'Aap_uEBit0r_5AzBMjdjfYZ-j_oWr9KracNlCQq5zsJO94fNiP3iT3TLc6LZQVKaz9jk2SXRWNKEq-kWyXa9bpASoenufZAAXEnTPz51H35JLdWagBVHz24jrqEv5dwqvjalJpG2hqzsdQ21_v7hVanLJYcZMKrYde92-auu4eu8RhjgpyzX'},
            {"photo_reference": 'Aap_uEB8CuwOEqkXSK7qFO2RlAURE0ahXh47SFdtMKo5Xk7XTQM1sVFByhYgRdHDQ5pUK-AdMRcfH3m0eDsrRe4jkxjkgEtx41cfdAZSBAUij5412738TRxTdZUp8a3miYkbznQ_JAEcVo4YNvkezrqaluxthmT7VF1i_NVZGJWJSIkEBzeg'},
            {"photo_reference": 'Aap_uED0hZcZiGQBAIW1qRjkSc82bVdcymwJ3lctanpGGjshaIZOMMdomTWcDFuicrWjNpv4PJjmd_Fhxd623lKVWZ26DEZFg0TDodMoCe0_wzlV6ogODcRFLA75rRa0i0bJPZIxT4Vehpdl0BEHubUxPdu4xuLLMXbGV3J-BpsMmHFrXqgf'}
        ]
    }

    time.sleep(0.1)
    # pprint.PrettyPrinter(indent=2).pprint(res)

    # if r_info.name is None: r_info.name = res.get("name")
    # if r_info.address is None: r_info.address = res.get("formatted_address")
    # if r_info.lat is None: r_info.lat = res.get("geometry")["location"]["lat"]
    # if r_info.lon is None: r_info.lon = res.get("geometry")["location"]["lng"]

    # r_info.google_rating = res.get("rating")
    # if res.get("reviews") is not None:
    #     r_info.review += [r["text"] for r in res.get("reviews")]

    r_info.google_photo_reference = [r["photo_reference"] for r in
                                     res.get("photos")]
    # TODO: xxxday_opening_hoursを取得する
    return r_info

def google_place_photo(photo_reference, image_width):
    """

    Parameters
    ----------
    photo_reference

    Returns
    -------
    image: Image
    """
    time.sleep(0.2)
    filename = 'test/data/Aap_uEDbtTwOXOryFJYq3129RPKnlC4JRe4XVjFWnqb3uT2aGsCHUdOW9_TetRCnFkaSnd3dWgrqfzjJYDUX1s5DK6blbKeZ780kfTV-t546Er998J5Wr1ddhaNwmZ9CvCivrKNllfzREoU1mqxcgqYvtUxsRAWAwHQDqh_Uw3DuPEv10U8m.png'
    image = Image.open(filename)

    return image



