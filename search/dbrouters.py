from search.models import SpinTextCache, PlaceStat


class DBRouter:

    def db_for_read(self, model, **hints):
        if model in (SpinTextCache, PlaceStat, ):
            return 'prop_db'
        return None

    def db_for_write(self, model, **hints):
        if model in (SpinTextCache, PlaceStat, ):
            return 'prop_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in ('spintextcache', 'placestat'):
            return db == 'prop_db'
        return db == 'default'
