from django.shortcuts import render
from django.http import HttpResponse
import pyodbc
import json
import datetime


def _get_config():
    with open('../config.json', 'r') as outfile:
         return  json.load(outfile)['database']

def json_default_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def index(req):

    database_config = _get_config()

    user = database_config['user']
    password = database_config['password']
    server = database_config['server']
    database = database_config['database']

    connection_string = \
        f'Driver={{ODBC Driver 17 for SQL Server}};' \
        f'Server={server};' \
        f'Database={database};' \
        f'UID={user};' \
        f'PWD={password}'

    sql_query = '''
        select
            decisao [DECISÃO]
            ,ementa [EMENTA]
            ,data_publicacao [DATA DA PUBLICAÇÃO]
            ,tema	[TEMA]
            ,tese	[TESE]
            ,data_julgamento [DATA DO JULGAMENTO]
            ,classe_processual [CLASSE PROCESSUAL]
            ,doutrina	[DOUTRINA]
            ,relator	[RELATOR]
            ,legislacao	[LEGISLAÇÃO]
        from 
            tb_jurisprudencia WITH(NOLOCK)
    '''
    # breakpoint()
    with  pyodbc.connect(connection_string, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            records = cursor.fetchall()
            result = []
            columnNames = [column[0] for column in cursor.description]
            for record in records:
                result.append(dict(zip(columnNames, record)))
                # result.append(list(record))

    # result = json.dumps(result, default=json_default_converter)
    # columnNames = json.dumps(columnNames, default=json_default_converter)


    dados = {
        'dados': result
        ,'cabecalho': columnNames
    }



    return render(req, 'index.html', dados)


