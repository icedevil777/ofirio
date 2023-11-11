from api_property.models import Building


class DBRouter:

    def db_for_read(self, model, **hints):
        if model in (Building, ):
            return 'prop_db'
        return None

    def db_for_write(self, model, **hints):
        if model in (Building, ):
            return 'prop_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in ('building',):
            return db == 'prop_db'
        return db == 'default'
