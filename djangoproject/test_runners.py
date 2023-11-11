from django.conf import settings
from django.db import connections
from django.test.runner import DiscoverRunner

from common.utils import read_text_file


class PortalTestRunner(DiscoverRunner):
    prepopulate_sql_files = (
        'djangoproject/test_sql/create_prop_cache.sql',
        'djangoproject/test_sql/populate_prop_cache.sql',
        'djangoproject/test_sql/create_geo_boundaries.sql',
        'djangoproject/test_sql/create_zip_boundaries.sql',
        'djangoproject/test_sql/create_mls_analytics.sql',
        'djangoproject/test_sql/create_seo_srp_links.sql',
        'djangoproject/test_sql/create_seo_srp_links_test.sql',
        'djangoproject/test_sql/create_spin_text_cache.sql',
        'djangoproject/test_sql/create_buildings.sql',
        'djangoproject/test_sql/create_buildings_sitemap.sql',
        'djangoproject/test_sql/populate_seo_links.sql',
        'djangoproject/test_sql/populate_seo_links_test.sql',
        'djangoproject/test_sql/populate_mls_analytics.sql',
        'djangoproject/test_sql/populate_geo_boundaries.sql',
        'djangoproject/test_sql/create_parsing_mls_mlsprovider.sql',
        'djangoproject/test_sql/create_parsing_mls_mlsconfig.sql',
        'djangoproject/test_sql/create_all_props.sql',
        'djangoproject/test_sql/create_price_history.sql',
        'djangoproject/test_sql/create_prop_photos.sql',
        'djangoproject/test_sql/populate_prop_photos.sql',
    )

    def populate_prop_db(self):
        """
        Create tables and populate with a few entries needed in tests
        """
        cursor = connections['prop_db'].cursor()
        for filepath in self.prepopulate_sql_files:
            sql_code = read_text_file(filepath)
            cursor.execute(sql_code)

    def setup_databases(self, **kwargs):
        """
        Replace PostgreSQL prop_db with in-memory SQLite, same way as 'default',
        and pre-populate it
        """
        settings.DATABASES['prop_db'] = {
            'ENGINE': 'common.custom_sqlite3_backend',
            'NAME': 'file:memorydb_prop_db?mode=memory&cache=shared',
        }
        settings.DATABASES['prop_db_rw'] = {
            'ENGINE': 'common.custom_sqlite3_backend',
            'NAME': 'file:memorydb_prop_db_rw?mode=memory&cache=shared',
        }
        old_names = super().setup_databases(**kwargs)
        self.populate_prop_db()
        return old_names
