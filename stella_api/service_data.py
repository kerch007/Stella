from collections import namedtuple
import json
import requests
import os
from database.db_connection import session_maker
from database.db_store_data_bot import db_store_start, db_get_fuel, db_store_recognized
from stella_api.imageMetadata.coordinates_metadata import MetaDataFromCoordinates
from stella_api.image_recognition import digit_to_price
from transport.data_provider import DropBoxDataProvider

TMP_IS_PREMIUM = False
TMP_IS_RECOGNIZED = True
TMP_IS_FROM_METADATA = False

dbx_token = os.environ['DROPBOX_TOKEN']
telegram_token = os.environ['TELEGRAM_TOKEN']

def store_bot_data(tg_id, image_link, latitude, longitude):
    md_from_coordinates = MetaDataFromCoordinates(latitude, longitude)
    company_name = md_from_coordinates.get_name()
    address = md_from_coordinates.get_address()

    session = session_maker()
    stored_data = db_store_start(session, tg_id, image_link, company_name, address)

    recognized_info = digit_to_price(image_link).split(',')
    is_recognized=recognized_info[0]
    if is_recognized:
        rec_fuel_type = recognized_info[1]
        is_premium = TMP_IS_PREMIUM
        fuel = db_get_fuel(session, rec_fuel_type, is_premium)
        if fuel is None:
            return "There isn't a fuel {} in database".format(rec_fuel_type)

        if recognized_info[2].replace('.', '', 1).isdigit():
            rec_price = float(recognized_info[2])
            recognition_result = namedtuple('rec_result', ['is_recognized', 'fuel_type', 'price'])
            rr = recognition_result(is_recognized, rec_fuel_type, rec_price)

            location_result = namedtuple('loc_result', ['gas_station', 'is_from_metadata'])
            lr = location_result(stored_data['gas_station'].id, TMP_IS_FROM_METADATA)
            db_store_recognized(session, stored_data['image'], rr, lr)
        else:
            return "{} is not a float number".format(recognized_info[2])
    else:
        return 'photo is not recognized'
    session.close()
    return 'Ok'


def upload_image_to_dbx(file_id):
    tg_file_link = f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}"
    tg_file = requests.get(tg_file_link)
    loaded_data = json.loads(tg_file.text)
    file_path = loaded_data["result"]["file_path"]

    tg_down_path = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
    dirname, basename = os.path.split(file_path)
    dbx_path = "/telegram_files/" + basename
    dbx_provider = DropBoxDataProvider(dbx_token)
    dbx_provider.file_upload(tg_down_path, dbx_path)
    return dbx_path
