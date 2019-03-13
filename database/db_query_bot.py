from datetime import date, datetime

from sqlalchemy.sql import func, subquery
from sqlalchemy.sql.expression import literal
from sqlalchemy.orm.query import Query


from database.models import FuelCompany, GasStation, Fuel, Price


def days_to_date(days) -> date:
    if isinstance(days, datetime):
        return days.date()
    if isinstance(days, date):
        return days
    try:
        return datetime.strptime(days, '%Y-%m-%d').date()
    except:
        return None


def get_date_subquery(session, days) -> subquery:
    days = days_to_date(days)
    if days is not None:
        subquery = session.query(literal(days).label("date_of_price")).subquery()
    else:
        subquery = session.query(func.date(func.max(Price.date_of_price)).label("date_of_price")).subquery()
    return subquery


def query_by_station_current_date(session, company_name, gas_station, days=None) -> Query:
    subquery = get_date_subquery(session, days)

    result = session.query(Price.price, GasStation.address, Price.date_of_price, Fuel.fuel_type
                           ).join(Fuel).join(GasStation
                           ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                           ).filter(FuelCompany.fuel_company_name == company_name
                           ).filter(GasStation.address == gas_station
                           ).filter(func.date(Price.date_of_price) == subquery.c.date_of_price)

    return result


def query_avg_all_stations(session, days=None) -> Query:
    subquery = get_date_subquery(session, days)
    result = session.query(func.avg(Price.price).label("average_price"),
                           Fuel.fuel_type, func.date(Price.date_of_price).label("date_of_price")
                           ).join(Fuel
                           ).filter(subquery.c.date_of_price == func.date(Price.date_of_price)
                           ).group_by(Fuel.fuel_type, func.date(Price.date_of_price)
                           ).order_by(Fuel.fuel_type)

    return result


def query_by_station_min_price(session, fuel_name, days=None) -> Query:
    subquery_date = get_date_subquery(session, days)
    result = session.query(Price.price, Price.date_of_price, Fuel.fuel_type, GasStation.address,
                           FuelCompany.fuel_company_name
                           ).join(Fuel).join(GasStation
                           ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                           ).filter(Fuel.fuel_type == fuel_name
                           ).filter(func.date(Price.date_of_price) == subquery_date.c.date_of_price
                           ).order_by(Price.price).limit(1)

    return result

def query_avg_price_period(session,fuel_name, day_from=None, day_to=None) -> Query:
    day_to = days_to_date(day_to)
    if day_to is None:
        day_to = datetime.today().date()
    day_from = days_to_date(day_from)
    if day_from is None:
        day_from=date(day_to.year, day_to.month, 1)
    result = session.query(func.avg(Price.price).label("average_price"),
                           Fuel.fuel_type, func.date(Price.date_of_price).label("date_of_price"),
                           FuelCompany.fuel_company_name
                           ).join(Fuel).join(GasStation
                           ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                           ).filter(Fuel.fuel_type == fuel_name
                           ).filter(func.date(Price.date_of_price).between(day_from, day_to)
                           ).group_by(Fuel.fuel_type, func.date(Price.date_of_price),FuelCompany.fuel_company_name
                           ).order_by(FuelCompany.fuel_company_name, func.date(Price.date_of_price))

    return result

def query_all_price_period(session, day_from=None, day_to=None) -> Query:
    day_to = days_to_date(day_to)
    if day_to is None:
        day_to = datetime.today().date()
    day_from = days_to_date(day_from)
    if day_from is None:
        day_from=date(day_to.year, day_to.month, 1)
    result = session.query(Price.price,
                           Fuel.fuel_type, Price.date_of_price,
                           FuelCompany.fuel_company_name,
                           GasStation.address
                           ).join(Fuel).join(GasStation
                           ).join(FuelCompany, FuelCompany.id == GasStation.fuel_company_id
                           ).filter(func.date(Price.date_of_price).between(day_from, day_to)
                           ).order_by(Price.date_of_price.desc(),Fuel.fuel_type,FuelCompany.fuel_company_name, )

    return result
