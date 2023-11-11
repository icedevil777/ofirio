import re

from django.db.backends.sqlite3 import base


class DatabaseWrapper(base.DatabaseWrapper):

    def create_cursor(self, name=None):
        return self.connection.cursor(factory=SQLiteCursorWrapper)


class SQLiteCursorWrapper(base.SQLiteCursorWrapper):
    """
    We want to emaulte PostgreSQL db using SQLite in tests.
    Django docs says: "Dictionary params are not supported with the SQLite backend;
    with this backend, you must pass parameters as a list"
    https://docs.djangoproject.com/en/3.2/topics/db/sql/#passing-parameters-into-raw

    So we basically convert them from dict to list before passing to the Django SQLite backend
    """

    def execute(self, query, params=None):
        if params and isinstance(params, dict):
            query, params = self.convert_params(query, params)
        query = query.replace(' now()', ' current_timestamp')
        query = re.sub(r"(\S+) ->> '(\S+)'", r"json_extract(\1, '$.\2')", query)
        query = re.sub(r"(\S+) -> (\d+)", r"json_extract(\1, '$[\2]')", query)
        return super().execute(query, params)

    def convert_params(self, query, params):
        """
        Convert SQL query with dictionary params to the one with list params,
        because Django SQLite backend supports only list params
        """
        new_query = ''
        new_params = []
        end = 0

        for q_param in re.findall('%\([a-zA-Z_\d]+?\)s', query):
            start = query.index(q_param)
            q_param_val = params[q_param[2:-2]]

            # Replace special cases manually in query
            # and don't add them to new_params
            if isinstance(q_param_val, tuple):
                token = self._convert_tuple(q_param_val)
            else:
                token = '%s'
                new_params.append(q_param_val)

            new_query += query[end:start] + token
            end = start + len(q_param)

        new_query += query[end:]
        return new_query, new_params

    def _convert_tuple(self, tuple_):
        """
        A tuple must not end with comma, it need to be deleted
        """
        tuple_ = str(tuple_)
        if tuple_[-2] == ',':
            tuple_ = tuple_[:-2] + ')'
        return tuple_
