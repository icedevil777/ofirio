import warnings
import logging
import time

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import OrdinalEncoder
from psycopg2.extras import execute_values, RealDictCursor
from ofirio_common.iterations import first_iteration
from ofirio_common.address_util import urlify
from ofirio_common.geocode import get_block_info

from common.utils import get_us_zips, calculate_distance
from common.constants import COMPARABLES_TYPE3_TO_UI
from api_property.common.common import cant_show_price_fields

warnings.filterwarnings('ignore')
logger = logging.getLogger("sale_estimator")


class SaleEstModel:
    def __init__(self, conn, data):
        self.conn = conn

        address = data["address"]
        self.prop_type3 = data["prop_type3"]
        self.beds = data["beds"]
        self.baths = data["baths"]
        self.state_id = address["state_id"]
        self.county = urlify(address["county"])
        self.city = urlify(address["city"])
        self.address_line = address.get("address_line") or data["query"]
        self.zip = address["zip"]
        self.building_size = data["building_size"]
        self.lat = address["lat"]
        self.lon = address["lon"]

        if data["prop_id"]:
            self.is_rehab = data["is_rehab"]
        else:
            self.is_rehab = False

        # these vars require db access and will be set later
        self.population = None
        self.block_id = None
        self.coastline = None
        self.cl_price = None
        self.cl_price_per_sqft = None
        self.bl_cl_price = None
        self.bl_cl_price_per_sqft = None
        self.filter_iter = ''

    def select_comps(self):
        sql = """
            select
                s.prop_id,
                s.state_id,
                s.zip,
                s.city,
                s.county,
                s.line address_line,
                s.lat,
                s.lon,
                s.beds,
                s.baths,
                s.block_id,
                s.building_size,
                s.prop_type3,
                s.close_date,
                s.close_price,
                s.is_rehab,
                b.coastline,
                u.population
            from sale_est s
            join blocks_geometry b using(block_id)
            join us_zips u using(zip)
            where
                s.state_id = %(state_id)s and
                s.city = %(city)s and
                s.prop_type3 = %(prop_type3)s and
                s.beds between %(beds)s - 1 and %(beds)s + 1 and
                s.baths between %(baths)s - 1 and %(baths)s + 1 and
                ST_DWithin(
                    Geography(ST_MakePoint(s.lon, s.lat)),
                    Geography(ST_MakePoint(%(lon)s, %(lat)s)),
                    5 * 1609.344)
        """
        if self.building_size and self.building_size > 0:
            sql += "and building_size between %(size)s - 500 and %(size)s + 500"
        sql += " limit 2000"
        params = {
            "state_id": self.state_id,
            "city": self.city,
            "prop_type3": self.prop_type3,
            "beds": self.beds,
            "baths": self.baths,
            "lat": self.lat,
            "lon": self.lon,
            "size": self.building_size,
        }
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, params)
            logger.debug(cursor.query.decode())
            df = pd.DataFrame(cursor.fetchall())
        return df

    def add_cols_to_comps(self, comparables):
        if len(comparables) < 5:
            # can't do prediction anyway
            return

        comparables["price_per_sqft"] = (
            comparables["close_price"] / comparables["building_size"]
        )
        comparables["month_from_today"] = np.ceil((time.time() - comparables["close_date"]) / (24 * 60 * 60 * 30))

        if comparables[comparables.month_from_today <= 6].shape[0] > 150:
            comparables.drop(comparables[comparables.month_from_today > 6].index, axis=0, inplace=True)
            self.filter_iter = '6m'
        comparables["quarter_from_today"] = np.ceil(comparables["month_from_today"] / 3)
        comparables["months_since"] = comparables["month_from_today"]
        comparables["distance"] = comparables.apply(
            lambda row: calculate_distance(
                row["lat"],
                row["lon"],
                self.lat,
                self.lon,
            ),
            axis=1,
        )
        if comparables[comparables.distance <= 2].shape[0] > 100:
            comparables.drop(comparables[comparables.distance > 2].index, axis=0, inplace=True)
            self.filter_iter += '2d'

        if comparables[comparables.month_from_today <= 3].shape[0] > 70:
            comparables.drop(comparables[comparables.month_from_today > 3].index, axis=0, inplace=True)
            if '2d' in self.filter_iter:
                self.filter_iter = '3m2d'
            else:
                self.filter_iter = '3m'
        self.add_stat_columns(comparables)

    def set_additional_vars(self):
        '''
        set vars that require db access:
            cl_price, cl_price_per_sqft,
            bl_cl_price, bl_cl_price_per_sqft,
            block_id, coastline, population
        '''
        if any((self.cl_price, self.cl_price_per_sqft,
                self.bl_cl_price, self.bl_cl_price_per_sqft)):
            # in unit test we set these vars manually
            return

        if block_info := get_block_info(self.conn, self.lat, self.lon):
            self.block_id = block_info['block_id']
            self.coastline = block_info['coastline']

        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if res := self.get_zip_stat(cursor, [[self.zip, 1]]):
                self.cl_price = res[0]["close_price"]
                self.cl_price_per_sqft = res[0]["close_price_sqft"]

            if res := self.get_block_stat(cursor, [[self.block_id, 1]]):
                self.bl_cl_price = res[0]["close_price"]
                self.bl_cl_price_per_sqft = res[0]["close_price_sqft"]

            cursor.execute(
                "select population from us_zips where zip = %s",
                (self.zip,)
            )
            if res := cursor.fetchone():
                self.population = res["population"]

    def get_zip_stat(self, cursor, values):
        """
        values is a list of [zip, month_from_today] pairs
        """
        sql = """
            select z.zip, z._month, z.close_price, z.close_price_sqft
            from zip_close_price z, (values %s) c (zip, month_from_today)
            where z.zip = c.zip and z._month = c.month_from_today
        """
        execute_values(cursor, sql, values)
        logger.debug(cursor.query.decode())
        return cursor.fetchall()

    def get_block_stat(self, cursor, values):
        """
        values is a list of [block_id, quarter_from_today] pairs
        """
        sql = """
            select z.block_id, z.quarter, z.close_price, z.close_price_sqft
            from block_close_price z, (values %s) c (block_id, quarter_from_today)
            where z.block_id = c.block_id and z.quarter = c.quarter_from_today
        """
        execute_values(cursor, sql, values)
        logger.debug(cursor.query.decode())
        return cursor.fetchall()

    def add_stat_columns(self, comparables):
        """
        Add cl_price, cl_price_per_sqft, bl_cl_price, bl_cl_price_per_sqft
        columns to comparables
        """
        # zip stat by months
        values = comparables[["zip", "month_from_today"]].drop_duplicates().values
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            res = self.get_zip_stat(cursor, values)
            stat_map = {
                (x["zip"], x["_month"]): (x["close_price"], x["close_price_sqft"])
                for x in res
            }
        comparables["cl_price"] = comparables.apply(
            lambda x: stat_map.get((x.zip, x.month_from_today), (None, None))[0],
            axis=1,
        )
        comparables["cl_price_per_sqft"] = comparables.apply(
            lambda x: stat_map.get((x.zip, x.month_from_today), (None, None))[1],
            axis=1,
        )

        # block_id stat by quaters
        values = (
            comparables[["block_id", "quarter_from_today"]].drop_duplicates().values
        )
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            res = self.get_block_stat(cursor, values)
            stat_map = {
                (x["block_id"], x["quarter"]): (x["close_price"], x["close_price_sqft"])
                for x in res
            }
        comparables["bl_cl_price"] = comparables.apply(
            lambda x: stat_map.get((x.block_id, x.quarter_from_today), (None, None))[0],
            axis=1,
        )
        comparables["bl_cl_price_per_sqft"] = comparables.apply(
            lambda x: stat_map.get((x.block_id, x.quarter_from_today), (None, None))[1],
            axis=1,
        )

    def get_lgbm_prediction(self, comparables) -> int:
        """returns estimated price"""
        pred_dict = {
            "beds": [self.beds],
            "baths": [self.baths],
            "building_size": [self.building_size],
            "month_from_today": [1],
            "cl_price": [self.cl_price],
            "bl_cl_price": [self.bl_cl_price],
            "cl_price_per_sqft": [self.cl_price_per_sqft],
            "bl_cl_price_per_sqft": [self.bl_cl_price_per_sqft],
            "population": [self.population],
            "zip": [self.zip],
            "block_id": [self.block_id],
            "coastline": [self.coastline],
            "city": [self.city],
            "is_rehab": [self.is_rehab],
            "distance": [0.01],
            "price_per_sqft": [self.cl_price_per_sqft],
            "close_price": [None],
        }
        df_pred = pd.DataFrame(pred_dict)


        features = comparables[
            [
                "beds",
                "baths",
                "building_size",
                "month_from_today",
                "cl_price",
                "bl_cl_price",
                "cl_price_per_sqft",
                "bl_cl_price_per_sqft",
                "population",
                "zip",
                "block_id",
                "coastline",
                "city",
                "is_rehab",
                "distance",
                "close_price",
                "price_per_sqft",
            ]
        ]

        features = pd.concat([features, df_pred])

        columns_to_remove = []
        for column in ['building_size', 'cl_price', 'bl_cl_price', 'cl_price_per_sqft','bl_cl_price_per_sqft','price_per_sqft']:
            if df_pred[column].values[0] is None or df_pred[column].values[0] == 0:
                columns_to_remove.append(column)
        features = features.drop(columns_to_remove, axis=1)
        enc = OrdinalEncoder()
        features[["zip", "block_id", "coastline", "city"]] = enc.fit_transform(
            features[["zip", "block_id", "coastline", "city"]]
        )
        # convert distance to discrete range 0, 1, .., 20 to use as category
        features["distance"] = np.ceil(features["distance"] / 0.5)

        target_features = features[features.close_price.isna()]
        features = features.drop(target_features.index)
        target = features["close_price"]
        features = features.drop(["close_price"], axis=1)
        target_features = target_features.drop(["close_price"], axis=1)
        categ = ['beds', 'baths', 'month_from_today', 'zip', 'block_id', 'coastline', 'city', 'is_rehab', 'distance']
        model = lgb.LGBMRegressor(random_state=666)
        model.fit(features,target.astype('int32'),categorical_feature = categ)
        return int(model.predict(target_features)[0])

    @property
    def prop_info(self) -> dict:
        '''
        debug info to verify prop location and block id
        '''
        return {
            "population": self.population,
            "block_id": self.block_id,
            "county": self.county,
            "city": self.city,
            "zip": self.zip,
            "lat": self.lat,
            "lon": self.lon,
        }

    def estimate(self, comparables) -> dict:
        res = {
            "qty": None,
            "pred_max": None,
            "pred_min": None,
            "est_price": None,
            "price_avg": None,
            "comparables": None,
            "percentile25": None,
            "percentile75": None,
            "price_median": None,
            "__method": '',
            "__info_analyze": None,
            "prop_info": self.prop_info,
        }

        if comparables.shape[0] < 5:
            return res

        iteration, frame_iter = first_iteration(
            frame=comparables,
            subdivision=None,
            prop_type3=self.prop_type3,
            beds=self.beds,
            baths=self.baths,
            building_size=self.building_size,
            lat=self.lat,
            lon=self.lon,
            year_built=None,
        )

        if iteration == 1:
            comparables = frame_iter
            res["__method"] = "first_iteration"
        else:
            try:
                self.set_additional_vars()
                res["est_price"] = self.get_lgbm_prediction(comparables)
                res["__method"] = "lgbm"
            except Exception as e:
                logger.warn("LGBM prediction failed")
                logger.exception(e)

        res["price_median"] = int(comparables.close_price.median())
        res["price_avg"] = int(comparables.close_price.mean())
        res["percentile25"] = int(comparables.close_price.quantile(0.25).mean())
        res["percentile75"] = int(comparables.close_price.quantile(0.75).mean())
        res["qty"] = comparables.shape[0]
        comparables = comparables.sort_values(by=["distance"], ascending=[True])
        res["comparables"] = comparables.head(20)
        res["__info_analyze"] = {'months': comparables.month_from_today.value_counts().to_dict(),
                                 'mean_dist' : comparables.distance.mean(),
                                 'max_dist' : comparables.distance.max(),
                                 'zips' : comparables.zip.value_counts().to_dict(),
                                 'cl_price_na' : comparables[comparables.cl_price.isna()].shape[0],
                                 'cl_pr_ft_na' : comparables[comparables.cl_price_per_sqft.isna()].shape[0],
                                 'bl_cl_price_na' : comparables[comparables.bl_cl_price.isna()].shape[0],
                                 'bl_pr_ft_na' : comparables[comparables.bl_cl_price_per_sqft.isna()].shape[0],
                                 'price_per_sqft_na': comparables[comparables.price_per_sqft.isna()].shape[0],
                                 'filter_iter' : self.filter_iter
                                 }


        if res["est_price"] is None:
            if (self.building_size and
                    comparables[comparables.price_per_sqft.isna()].shape[0] == 0):
                price_per_sqft = comparables.price_per_sqft.mean()
                price = round(price_per_sqft * self.building_size)
                res["est_price"] = int((res["price_median"] + price) / 2)
                res["__method"] += "_mean"
            else:
                res["est_price"] = res["price_median"]
                res["__method"] += "_median"

        res["pred_min"] = int(
            comparables.close_price.min()
            if comparables.close_price.min() < res["est_price"]
            else round(res["est_price"] * 0.8)
        )
        res["pred_max"] = int(
            comparables.close_price.max()
            if comparables.close_price.max() > res["est_price"]
            else round(res["est_price"] * 1.2)
        )
        res["prop_info"] = self.prop_info
        return res

    def comparables_to_ui(self, comparables) -> list:
        # TODO: very similar to rent analyzer. make common method
        items = []
        if comparables is None:
            return items
        median = comparables.close_price.median()
        comparables['price_per_sqft'] = (comparables['price_per_sqft']
            .fillna(np.nan)
            .replace([np.nan, np.inf], [None, None])
        )
        for row in comparables.itertuples():
            if row.close_price > median * 1.05:
                _type = 'higher'
            elif row.close_price < median * 0.95:
                _type = 'lower'
            else:
                _type = 'moderate'

            if row.distance and not np.isnan(row.distance):
                distance = round(row.distance, 2)
            else:
                distance = None

            can_show_price = not cant_show_price_fields('closed', row.state_id)
            if row.building_size and can_show_price:
                price_per_ft2 = round(row.price_per_sqft, 2)
            else:
                price_per_ft2 = None
            items.append({
                'state_id': row.state_id,
                'zip': row.zip,
                'address': row.address_line,
                'location': str((row.lat, row.lon)),
                'beds': row.beds,
                'baths': row.baths,
                'prop_type3': COMPARABLES_TYPE3_TO_UI.get(row.prop_type3),
                'building_size': row.building_size if row.building_size > 0 else None,
                'price_per_ft2': price_per_ft2,
                'price': row.close_price if can_show_price else None,
                'type': _type,
                'distance': distance,
                'close_date': pd.to_datetime(row.close_date, unit='s'),
            })
        return items


    def get_prediction(self):
        """main method accessible via api"""
        comparables = self.select_comps()
        self.add_cols_to_comps(comparables)
        res = self.estimate(comparables)
        res["comparables"] = self.comparables_to_ui(res["comparables"])
        return res
