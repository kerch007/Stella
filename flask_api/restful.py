import json
from flask import request, Blueprint
from database.db_query_bot import (query_by_station_min_price, query_by_station_current_date, query_avg_all_stations)
from flask_api import helpers
from stella_api.imageMetadata.coordinates_metadata import MetaDataFromCoordinates
from stella_api.service_data import upload_image_to_dbx
from flask_login import login_required


restful = Blueprint('restful', __name__, url_prefix='/restful')


@restful.route('/min_by_fuel', methods=['GET'])
@login_required
def min_price():
    if request.is_json:
        request_data = request.get_json()
    fuel_type = request_data["fuel_type"]
    date_of_price = request_data["date_of_price"]
    result = query_by_station_min_price(fuel_type, date_of_price)
    result_dict = helpers.query_to_dict(result)
    return json.dumps(result_dict, cls=helpers.QueryEncoder, ensure_ascii=False)


@restful.route('/price_by_day', methods=['GET'])
@login_required
def price_by_day():
    if request.is_json:
        request_data = request.get_json()
    long = request_data["longitude"]
    lat = request_data["latitude"]
    date_of_price = request_data["date_of_price"]
    company = MetaDataFromCoordinates(lat, long)
    company_name = company.get_name()
    company_address = company.get_address()
    result = query_by_station_current_date(company_name, company_address, date_of_price)
    result_dict = helpers.query_to_dict(result)
    return json.dumps(result_dict, cls=helpers.QueryEncoder, ensure_ascii=False)


@restful.route('/avg_price', methods=['GET'])
@login_required
def avg_price():
    if request.is_json:
        request_data = request.get_json()
    date_of_price = request_data["date_of_price"]
    result = query_avg_all_stations(date_of_price)
    result_dict = helpers.query_to_dict(result)
    return json.dumps(result_dict, cls=helpers.QueryEncoder, ensure_ascii=False)


@restful.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    if request.is_json:
        request_data = request.get_json()
    file_id = request_data["file_id"]
    dbx_path = upload_image_to_dbx(file_id)
    return json.dumps({"dropbox_path": dbx_path})