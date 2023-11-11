import logging
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from django.conf import settings
from django.db import connections
from django.utils.module_loading import import_string
from psycopg2.extras import RealDictCursor
from ofirio_common.median_query_sql import get_median_query_sql
from ofirio_common.geocode import geocode, parse_address_from_geocode
from ofirio_common.iterations import iteration_selection, baths_filter
from ofirio_common.constants import closed_statuses, closed_statuses_rent_est
from ofirio_common.states_constants import states_from_short

from api_property.common.common import (
    getProp,
    getPropAddressStr,
    get_us_blocks,
    func_point2,
    block_number,
    cant_show_price_fields,
)
from common.utils import get_pg_connection
from common.constants import COMPARABLES_TYPE3_TO_UI
from rent_analyzer.enums import Baths, Beds, Distance, SearchType, PropertyType3


logger = logging.getLogger("rent_analyzer")


class RentAnalyzerCalculation:
    """Common logic and attributes for Mock and Real Calculation classes"""

    # INPUT PARAMS
    type = None
    query = None
    distance = None
    beds = None
    baths = None
    prop_type3 = None
    look_back = None
    building_size = None
    prop_id = None

    # ADDRESS RESULT
    address = None

    # RESULT
    found = False
    rent = False
    stat = False
    tables = False
    items = False

    def __init__(
        self,
        type,
        query,
        distance,
        beds,
        baths,
        prop_type3,
        look_back,
        building_size,
        prop_id,
    ):

        logger.info("-" * 30 + "Rent Analyzer started" + "-" * 30)
        self.prop_id = prop_id
        self.cursor = connections["prop_db"].cursor()

        # In case of prop_id, get params from property
        if self.prop_id:

            # PROP SEARCH
            prop = getProp(self.prop_id)
            if not prop:
                logger.info('Could not find property by id "%s"', self.prop_id)
                return

            self.prop_type3 = prop["data"]["prop_type3"]
            self.building_size = prop["data"]["building_size"]
            self.beds = prop["data"]["beds"]
            self.baths = prop["data"]["baths"]
            self.year_built = prop["data"]["year_built"]
            self.sale_price = prop["data"]["price"]
            self.address = {
                "state_name": states_from_short.get(prop["address"]["state_code"]),
                "state_id": prop["address"]["state_code"],
                "county": prop["address"]["county"],
                "city": prop["address"]["city"],
                "zip_code": prop["address"]["zip"],
                "lat": prop["address"]["lat"],
                "lon": prop["address"]["lon"],
                "place_type": "street_address",
                "formatted_address": getPropAddressStr(prop),
            }
            self.distance = 10
            self.look_back = 12

        else:
            # QUERY SEARCH
            self.type = type
            self.query = query
            self.distance = distance
            self.beds = beds
            self.baths = baths
            # TODO: dropdown in UI only accepts type2 values
            self.prop_type3 = prop_type3
            self.look_back = look_back
            self.building_size = building_size

            # GEO Query
            is_detect_address = self.geoQuery()
            if not is_detect_address:
                return

        logger.info("Model params: %s", vars(self))

        self.calculate()
        logger.info("-" * 30 + "Rent Analyzer completed" + "-" * 30)

    def geoQuery(self):
        raise NotImplementedError

    def calculate(self):
        raise NotImplementedError


class RealRentAnalyzerCalculation(RentAnalyzerCalculation):

    def geoQuery(self):
        logger.info('Trying to geocode query "%s"', self.query)
        cursor = connections["prop_db_rw"].cursor()
        location = geocode(cursor, address=self.query)
        if not location:
            logger.info("Location not found")
            self.address = None
            return
        self.address = parse_address_from_geocode(location)
        return True

    def calculate(self):
        if self.prop_id:
            SQL_comparables = """
                select comparables
                from postprocessed_sales
                where prop_id = %(prop_id)s
            """
            sql_comparables_params = {"prop_id": self.prop_id}
            self.cursor.execute(SQL_comparables, sql_comparables_params)
            res_comparable = self.cursor.fetchone()
            comparables = None
            if res_comparable and res_comparable[0]:
                comparables = json.loads(res_comparable[0])
            if not comparables:
                logger.info("Not found comparables from median_query")
                self.found = False
                return

            comps = ()
            for type_source in comparables:
                if type_source in ["mls", "compass"]:
                    comps += tuple(comparables[type_source])
            custom_condition = " WHERE prop_id in %(comparables)s "
            cursor = get_pg_connection().cursor(cursor_factory=RealDictCursor)
            SQL = get_median_query_sql(
                cursor,
                zip_code=self.address["zip_code"],
                custom_condition=custom_condition,
            )
            params = {
                "comparables": comps,
                "lat": self.address["lat"],
                "lon": self.address["lon"],
            }
            cursor.execute(SQL, params)
            frame = pd.DataFrame(cursor.fetchall())
            logger.info(f"LOG COMPS {comparables=}")
            logger.info(f"LOG COMPS {comps=}")
            logger.info(f"LOG COMPS {frame.shape[0]=}")

            min_qty = len(comps)
            if frame.shape[0] < min_qty:
                logger.info("Frame shape < ", min_qty, " after check comparables")
                self.found = False
                return

            if (self.building_size > 0
                    and frame[frame.building_size > 0].shape[0] == frame.shape[0]):
                frame["size_diff"] = frame["building_size"].apply(
                    lambda val: abs(self.building_size - val)
                )
                frame = frame.sort_values(
                    by=["distance", "size_diff"], ascending=[True, True]
                )
            else:
                frame = frame.sort_values(by=["distance"], ascending=[True])

            max_qty_calc = 35
            if frame.shape[0] >= max_qty_calc:
                frame = frame.head(max_qty_calc)

            if frame.shape[0] >= min_qty:
                self.rent = {}
                self.rent["average"] = frame.price.mean()
                self.rent["median"] = frame.price.median()

                if (self.building_size > 0
                        and frame[~frame.price_per_sqft.isna()].shape[0] == frame.shape[0]):
                    price_per_sqft = frame.price_per_sqft.mean()
                    pred_rent = round(price_per_sqft * self.building_size, 0)
                    self.rent["prediction"] = (self.rent["median"] + pred_rent) / 2
                else:
                    self.rent["prediction"] = self.rent["median"]

                month_lookback = comparables["month_lookback"]
                frame = frame.dropna(subset=["distance"])
                rentFrame = frame.copy()
            else:
                logger.info("Final frame shape < ", min_qty)
                self.found = False
                return

        else:
            # Speed up search, using only search in nearby zips, if zip code is available
            if zip_code := (self.address.get("zip_code") or self.address.get("zip")):
                path = settings.BASE_DIR / "data" / "uszips-cached.csv"
                zipFrame = pd.read_csv(path, converters={"zip": str})
                zipFrame = zipFrame.set_index("zip")
                nearby_zips = zipFrame.at[zip_code, "nearby_zips"]
            else:
                nearby_zips = ""

            prop_statuses = closed_statuses + closed_statuses_rent_est

            if self.type == SearchType.ADDRESS:
                limit = 2000  # was 35 - we limit later
                if self.distance == Distance.AUTO:
                    max_distance = 10.05  # for address max distance 10
                else:
                    max_distance = float(self.distance)

            if self.type == SearchType.ZIP or self.address["place_type"] == "zip":
                limit = 2000
                nearby_zips = str(zip_code)  # only current zip
                if self.distance == Distance.AUTO:
                    max_distance = 20
                else:
                    max_distance = float(self.distance)

            if self.type == SearchType.CITY or self.address["place_type"] == "city":
                limit = 2000
                if self.distance == Distance.AUTO:
                    max_distance = 20
                else:
                    max_distance = float(self.distance)

            if self.address["place_type"] in ("county", "state", "country"):
                limit = 2000
                nearby_zips = ""
                zip_code = None
                if self.distance == Distance.AUTO:
                    max_distance = 20
                else:
                    max_distance = float(self.distance)

            cursor = get_pg_connection().cursor(cursor_factory=RealDictCursor)
            SQL = get_median_query_sql(
                cursor,
                zip_code=zip_code,
                nearby_zips=nearby_zips,
                prop_type3=self.prop_type3,
            )
            SQL += " LIMIT %(limit)s "

            sql_params = {
                "lat": self.address["lat"],
                "lon": self.address["lon"],
                "source": ("compass", "mls"),
                "state_id": self.address["state_id"],
                "nearby_zips": tuple([str(item) for item in nearby_zips.split(",")]),
                "prop_type3": self.prop_type3,
                "prop_statuses": tuple([str(item) for item in prop_statuses]),
                "look_back": int(self.look_back),
                #'distance':        self.distance,
                "limit": limit,
            }

            cursor.execute(SQL, sql_params)
            rentFrame = pd.DataFrame(cursor.fetchall())
            logger.info("SQL query returned %s records", len(rentFrame))

            # NOT FOUND
            if rentFrame.shape[0] == 0:
                logger.info("Request data not found in prop_db")
                self.found = False
                return

            rentFrame = rentFrame.dropna(subset=["distance"])
            rentFrame = rentFrame[rentFrame["distance"] <= max_distance]
            logger.info(
                "After filter by max distance (%s): %s records",
                max_distance, len(rentFrame),
            )

            rentFrame.set_index("prop_id", inplace=True)

            # Remove incorrect years
            rentFrame["update_date"] = pd.to_datetime(
                rentFrame["update_date"], infer_datetime_format=True, errors="coerce"
            )

            rentFrame = rentFrame[
                rentFrame["update_date"].dt.year <= datetime.now().year
            ]  # remove futures years

            # REMOVE NA
            na_qty = rentFrame["update_date"].isna().sum()
            if na_qty:
                # print(' ' * 4, 'Found NA in rentFrame: ', na_qty)
                rentFrame = rentFrame.dropna(subset=["update_date"])

            # Calc month since
            months_since = (datetime.now() - rentFrame["update_date"]) / timedelta(
                days=30 * 1
            )
            rentFrame["months_since"] = round(months_since, 0)

            # Identify nearest blocks
            if self.address["place_type"] == "street_address":
                blockFrame = get_us_blocks(self.address["state_id"])
                point_coords = func_point2(self.address["lat"], self.address["lon"])
                if blockFrame is not None:
                    block_id = block_number(point_coords, blockFrame)
                else:
                    block_id = None
                list_nearby_blocks = None
                if block_id is not None:
                    coastline = blockFrame.at[block_id, "coastline"]
                    list_nearby_blocks = blockFrame.at[block_id, "nearby_bl"].split()
                    coast_line_list = blockFrame[
                        blockFrame.coastline == coastline
                    ].index.tolist()
                    rentFrame = rentFrame[rentFrame.block_id.isin(coast_line_list)]
            else:
                block_id = None
                list_nearby_blocks = None

            rentFrame["beds"] = rentFrame["beds"].apply(
                lambda row: 5 if row >= 5 else row
            )
            rentFrame["baths"] = rentFrame["baths"].apply(baths_filter)

            # STRIP FRAME USING SEARCH CONDITIONS
            if self.baths != Baths.ANY:
                if self.baths == Baths.FOUR_PLUS:
                    self.baths = 4
                self.baths = float(self.baths)

            if self.beds != Beds.ANY:
                if self.beds == Beds.FIVE_PLUS:
                    self.beds = 5
                self.beds = int(self.beds)

            if self.prop_type3 != PropertyType3.ANY:
                rentFrame = rentFrame[(rentFrame.prop_type3 == self.prop_type3)]

            frame = rentFrame

            if (self.type == SearchType.ZIP or self.type == SearchType.CITY
                    or self.address["place_type"] in ["zip", "city", "county", "state", "country"]):
                if self.beds != Beds.ANY:
                    frame = frame[frame.beds == self.beds]
                if self.baths != Baths.ANY:
                    frame = frame[frame.baths == self.baths]
                if self.building_size:
                    frame = frame[
                        (frame.building_size >= int(self.building_size - 500))
                        & (frame.building_size <= int(self.building_size + 500))
                    ]
                if self.look_back:
                    frame = frame[frame["months_since"] <= int(self.look_back)]
                if frame.shape[0] < 5:
                    return

            # DETECT DISTANCE IN CASE OF AUTO DISTANCE
            if (self.type == SearchType.ADDRESS
                    and self.address["place_type"] == "street_address"):
                list_look_back_month = [3, 6, 9, 12, 18, 24, 36, 48]
                look_back_ui = int(self.look_back)
                if look_back_ui < 3:
                    look_back_ui = 3

                list_look_back_month = [
                    x for x in list_look_back_month if x <= look_back_ui
                ]
                for look_back_month in list_look_back_month:
                    frame_look_back = frame[frame["months_since"] <= look_back_month]
                    if frame_look_back.shape[0] < 3:
                        continue
                    frame_look_back, iteration, _ = iteration_selection(
                        frame_look_back,
                        self.address["formatted_address"],
                        self.prop_type3,
                        self.beds,
                        self.baths,
                        self.building_size,
                        self.address["lat"],
                        self.address["lon"],
                        None,
                        block_id,
                        list_nearby_blocks,
                    )
                    if frame_look_back is not None:
                        break

                frame = frame_look_back

                if frame is None:
                    self.found = False
                    return

            if (self.building_size
                    and frame[frame.building_size > 0].shape[0] == frame.shape[0]):
                frame["size_diff"] = frame["building_size"].apply(
                    lambda val: abs(self.building_size - val)
                )
                frame = frame.sort_values(
                    by=["distance", "size_diff"], ascending=[True, True]
                )
            else:
                frame = frame.sort_values(
                    by=["distance", "months_since"], ascending=[True, True]
                )

            # COUNT FILTER
            if self.type == SearchType.ADDRESS:
                max_qty_calc = 35
                if frame.shape[0] >= max_qty_calc:
                    frame = frame.head(max_qty_calc)

            # SEARCH PROCESSING
            self.rent = {}
            self.rent["average"] = frame.price.mean()
            self.rent["median"] = frame.price.median()

            if (self.building_size
                    and frame[~frame.price_per_sqft.isna()].shape[0] == frame.shape[0]):
                price_per_sqft = frame.price_per_sqft.mean()
                pred_rent = round(price_per_sqft * self.building_size, 0)
                self.rent["prediction"] = (self.rent["median"] + pred_rent) / 2
            else:
                self.rent["prediction"] = self.rent["median"]

            month_lookback = frame.months_since.max()
            rentFrame = frame.copy()

        # NOT FOUND
        if rentFrame.shape[0] == 0:
            logger.info("Property was not found after all the calculation")
            self.found = False
            return
        else:
            self.found = True

        self.rent["percentile25"] = rentFrame.price.quantile(0.25).mean()
        self.rent["percentile75"] = rentFrame.price.quantile(0.75).mean()
        self.rent["min"] = (
            rentFrame.price.min()
            if rentFrame.price.min() < self.rent["prediction"]
            else round(self.rent["prediction"] * 0.8)
        )
        self.rent["max"] = (
            rentFrame.price.max()
            if rentFrame.price.max() > self.rent["prediction"]
            else round(self.rent["prediction"] * 1.2)
        )

        self.stat = {}
        self.stat["qty"] = rentFrame.shape[0]
        self.stat["max_dist"] = round(rentFrame.distance.max(), 2)
        self.stat["month_lookback"] = month_lookback

        median = rentFrame.price.median()

        # RETURN ITEMS
        items = []
        rentFrame = rentFrame.head(20)
        rentFrame["price_per_sqft"] = (
            rentFrame["price_per_sqft"].fillna(np.nan).replace([np.nan], [None])
        )
        for row in rentFrame.itertuples():
            if row.price > median * 1.05:
                type = "higher"
            elif row.price < median * 0.95:
                type = "lower"
            else:
                type = "moderate"
            can_show_price = not cant_show_price_fields(
                "closed", row.address_state_code
            )

            items.append({
                "state_id": row.address_state_code,
                "zip": row.address_zip,
                "address": row.address_line,
                "location": row.location,
                "beds": row.beds,
                "baths": row.baths,
                "prop_type3": COMPARABLES_TYPE3_TO_UI.get(row.prop_type3),
                "building_size": row.building_size,
                "price_per_ft2": (
                    round(row.price / row.building_size, 2)
                    if row.building_size and can_show_price
                    else 0
                )
                if can_show_price
                else None,
                "price": row.price if can_show_price else None,
                "type": type,
                "distance": round(row.distance, 2),
                "close_date": row.update_date,
            })

        # Shuffle items and get first 20
        # random.shuffle(items)
        # items = items[:20]

        self.items = items


class MockRentAnalyzerCalculation(RentAnalyzerCalculation):
    """
    Fake calculation class with hardcoded values to use in tests.
    It is automatically used in test by settings.RENT_ANALYZER_CALCULATION_MODEL var
    """

    found = True
    address = {
        "state_name": "Florida",
        "state_id": "FL",
        "city": "Miami",
        "zip_code": "",
        "lat": 25.7616798,
        "lon": -80.1917902,
        "formatted_address": "Miami, FL, USA",
    }
    rent = {
        "average": 2498.8,
        "median": 1962.5,
        "prediction": 1962.5,
        "percentile25": 1775.0,
        "percentile75": 2900.0,
        "min": 1250,
        "max": 8500,
    }
    stat = {"qty": 50, "max_dist": 3.00492479702117}
    tables = {
        "histogram": {
            "titles": [
                "$1250-$1975",
                "$1975-$2700",
                "$2700-$3425",
                "$3425-$4150",
                "$4150-$4875",
                "$4875-$5600",
                "$5600-$6325",
                "$6325-$7050",
                "$7050-$7775",
                "$7775-$8500",
            ],
            "values": [25, 9, 11, 1, 0, 1, 2, 0, 0, 1],
        },
        "rent_by_size": {
            "titles": [
                0, 485, 560, 567, 600, 670, 694, 714, 722, 730, 750, 795, 831, 851, 875, 878, 900,
                903, 906, 914, 917, 985, 1030, 1125, 1222, 1253, 1255, 1274, 1287, 1302, 1360,
                1395, 1524, 1538, 1663, 1664, 1797, 1831, 1950, 2069, 2195, 2331, 3225,
            ],
            "median": [
                1950, 1275, 1975, 1750, 1250, 1625, 1475, 2200, 1850, 1675, 1825, 1950, 1800, 1600,
                1750, 2800, 1950, 1895, 3800, 2550, 1862, 1875, 1950, 2000, 3000, 5200, 2900, 3000,
                3000, 5750, 2100, 3200, 3000, 2800, 1375, 2995, 8500, 3000, 2550, 2900, 2200, 6000,
                1650,
            ],
            "offers": [
                3, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1,
                1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            ],
        },
        "rent_by_type": {
            "titles": ["condo-apt", "house-duplex"],
            "median": [1922, 2998],
            "offers": [36, 14],
        },
        "rent_by_beds": {
            "titles": [0.0, 1.0, 2.0, 3.0, 4.0],
            "median": [1750, 1762, 2050, 3000, 5750],
            "offers": [1, 18, 22, 8, 1],
        },
    }
    items = [
        {
            "state_id": "FL",
            "zip": "33131",
            "address": "nan, Miami, FL, 33131",
            "location": "(25.763902,-80.191732)",
            "beds": 1.0,
            "baths": 2.0,
            "prop_type3": "condo-apt",
            "building_size": 906,
            "price_per_ft2": 4.19,
            "price": 3800,
            "type": "higher",
            "distance": 0.153574507731696,
        },
        {
            "state_id": "FL",
            "zip": "33130",
            "address": "3685 Southwest 3rd Avenue, Unit 3685, Miami, FL, 33145",
            "location": "(25.761037,-80.194399)",
            "beds": 1.0,
            "baths": 1.0,
            "prop_type3": "house-duplex",
            "building_size": 560,
            "price_per_ft2": 3.53,
            "price": 1975,
            "type": "moderate",
            "distance": 0.168293664124558,
        },
        {
            "state_id": "FL",
            "zip": "33145",
            "address": "2160 Southwest 16th Avenue, Unit 417, Miami, FL, 33145",
            "location": "(25.7517159,-80.220952)",
            "beds": 1.0,
            "baths": 1.0,
            "prop_type3": "condo-apt",
            "building_size": 694,
            "price_per_ft2": 2.16,
            "price": 1500,
            "type": "lower",
            "distance": 1.94080597849756,
        },
    ]

    def __init__(
        self,
        type,
        query,
        distance,
        beds,
        baths,
        prop_type3,
        look_back,
        building_size,
        prop_id,
    ):
        # Values to simulate errors in test cases. Feel free to change,
        # but remember to change the tests accordingly
        if "miami" not in query:
            self.found = False
        if distance == "10":
            self.address = None

    def geoQuery(self):
        return True

    def calculate(self):
        pass


def get_rent_analyzer_calculation_model():
    """Use this function to get the actual calculation class"""
    try:
        calculation_class = import_string(settings.RENT_ANALYZER_CALCULATION_MODEL)
    except (AttributeError, ImportError):
        # in case of error try to load real model
        path = "rent_analyzer.common.rent_analyzer_model.RealRentAnalyzerCalculation"
        calculation_class = import_string(path)
    return calculation_class
