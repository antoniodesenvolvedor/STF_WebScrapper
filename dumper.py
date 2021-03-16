import pyodbc
import json


class Dumper:
    def __init__(self):
        self._database_config = self._get_config()['database']

        user = self._database_config['user']
        password = self._database_config['password']
        server = self._database_config['server']
        database = self._database_config['database']

        connection_string = \
            f'Driver={{ODBC Driver 17 for SQL Server}};' \
            f'Server={server};' \
            f'Database={database};' \
            f'UID={user};' \
            f'PWD={password}'

        connection = pyodbc.connect(connection_string,autocommit=True)
        self._cursor = connection.cursor()




    def _get_config(self):
        with open('config.json', 'r') as outfile:
            return json.load(outfile)

    def executemany(self, sql, parameters):
        return self._cursor.executemany(sql, parameters)

    def execute(self, sql, parameters=None):
        if(parameters):
            return self._cursor.execute(sql, parameters)
        else:
            return self._cursor.execute(sql)

