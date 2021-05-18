from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from urllib.parse import urlencode
import pyodbc
import json
import datetime
from django.http import JsonResponse
from graylog import Graylog



def _return_connection_string():
    database_config = _get_config()

    user = database_config['user']
    password = database_config['password']
    server = database_config['server']
    database = database_config['database']

    return \
        f'Driver={{ODBC Driver 17 for SQL Server}};' \
        f'Server={server};' \
        f'Database={database};' \
        f'UID={user};' \
        f'PWD={password}'

def _get_config():
    with open('./config.json', 'r') as outfile:
         return  json.load(outfile)['database']

def json_default_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def _send_log_message(message):
    gray_log = Graylog()
    gray_log.log(str(message))



def cadastrar_carga(key_word):

    try:
        connection_string = _return_connection_string()

        sql_query = '''
          set nocount on
          INSERT INTO TB_LOTE (NOME_CARGA,DATACAD) VALUES (
                'Pesquisa: ' + ?
                ,getdate()
            )
            insert into TB_LOTE_LINHA (idlote,idstatus,datacad,historico)
            values (SCOPE_IDENTITY(),1,getdate(),'Carga cadastrada ||')
            
            insert into STF.TB_BUSCA_JURISPRUDENCIA (PALAVRA_CHAVE,datacad,IDLINHA) output inserted.IDBUSCA
            values (?,getdate(),SCOPE_IDENTITY())
           '''
        # breakpoint()
        with  pyodbc.connect(connection_string, autocommit=False) as connection:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(sql_query, (key_word,key_word))
                    idbusca = cursor.fetchall()
                    connection.commit()

                except:
                    connection.rollback()
                    raise
    except Exception as e:
        _send_log_message(e)
        raise

    return idbusca


def aguardar_captura(req):
    id_busca = req.GET.get('id_busca')
    key_word = req.GET.get('key_word')

    dados = {
        'id_busca': id_busca
        ,'key_word': key_word
    }

    return render(req, 'aguardando_captura.html', dados)


def return_progress(req):
    id_busca = req.GET.get('id_busca')
    key_word = req.GET.get('key_word')

    try:
        connection_string = _return_connection_string()

        sql_query = '''
            SELECT
                CASE
                    WHEN IDSTATUS = 1
                        THEN 0
                    WHEN IDSTATUS <> 1 AND TOTAL IS NOT NULL
                        THEN
                            ISNULL(count(retorno.idretorno),0) / CAST( TOTAL AS FLOAT) * 100	
                END			[progresso]
                ,LINHA.DATA_INICIO_PROCESSAMENTO data_inicio_processamento
            FROM
                STF.TB_BUSCA_JURISPRUDENCIA BUSCA 
                INNER JOIN TB_LOTE_LINHA LINHA ON LINHA.IDLINHA = BUSCA.IDLINHA
                LEFT JOIN STF.TB_RETORNO_JURISPRUDENCIA RETORNO ON RETORNO.IDBUSCA = BUSCA.IDBUSCA
            where
                busca.IDBUSCA = ?
            group by
                busca.total
                ,LINHA.IDSTATUS
                ,LINHA.data_inicio_processamento
    
            '''
        # breakpoint()

        progresso = None
        inicio_processamento = None
        with  pyodbc.connect(connection_string, autocommit=True) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_query, id_busca)
                records = cursor.fetchall()

                if(records):
                    records = records[0]
                    progresso = records[0]

                    inicio_processamento = records[1]

                    if inicio_processamento:
                        inicio_processamento = inicio_processamento.strftime("%m/%d/%Y, %H:%M:%S")
                    else:
                        inicio_processamento = 'Pendente'


    except Exception as e:
        _send_log_message(e)
        raise

    data = {
        'progress': progresso,
        'inicio_processamento': inicio_processamento
    }
    return JsonResponse(data)


def pesquisa(request):
    try:
        key_word = request.POST['key_word']
        idbusca = cadastrar_carga(key_word)[0][0]
        base_url = reverse('aguardar_captura')
        query_string = urlencode(
            {
                'key_word': key_word,
                'id_busca': idbusca

             }
        )
    except Exception as e:
        _send_log_message(e)
        raise

    return redirect(base_url +'?'+query_string)









def index(req):

    key_word = req.GET.get('key_word')

    connection_string = _return_connection_string()

    sql_query = '''
    SELECT
    	row_number()over(order by retorno.idretorno desc) [N°]
        ,decisao [DECISÃO]
        ,ementa [EMENTA]
        ,data_publicacao [DATA DA PUBLICAÇÃO]
        ,tema	[TEMA]
        ,tese	[TESE]
        ,data_julgamento [DATA DO JULGAMENTO]
        ,classe_processual [CLASSE PROCESSUAL]
        ,doutrina	[DOUTRINA]
        ,relator	[RELATOR]
        ,legislacao	[LEGISLAÇÃO]
        ,BUSCA.PALAVRA_CHAVE
    FROM		
        TB_LOTE LOTE WITH(NOLOCK)
        INNER JOIN TB_LOTE_LINHA LINHA WITH(UPDLOCK) ON LOTE.IDLOTE = LINHA.idlote
        INNER JOIN STF.TB_BUSCA_JURISPRUDENCIA BUSCA WITH(NOLOCK) ON BUSCA.IDLINHA = LINHA.IDLINHA
        LEFT JOIN STF.TB_RETORNO_JURISPRUDENCIA RETORNO WITH(NOLOCK) ON RETORNO.IDBUSCA = BUSCA.IDBUSCA
    WHERE
        LINHA.IDSTATUS = 4
        AND BUSCA.PALAVRA_CHAVE = ?
        AND lote.IDLOTE in (
			SELECT
				TOP 1
				LOTE.IDLOTE
			FROM
			    TB_LOTE LOTE WITH(NOLOCK)
				INNER JOIN TB_LOTE_LINHA LINHA WITH(UPDLOCK) ON LOTE.IDLOTE = LINHA.IDLOTE
				INNER JOIN STF.TB_BUSCA_JURISPRUDENCIA BUSCA WITH(NOLOCK) ON BUSCA.IDLINHA = LINHA.IDLINHA
			WHERE
				BUSCA.PALAVRA_CHAVE = ?
				AND LINHA.IDSTATUS = 4
			ORDER BY LOTE.IDLOTE DESC
		)
    '''
    # breakpoint()
    print(f'key_word: {key_word}')
    with  pyodbc.connect(connection_string, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_query, (key_word, key_word))
            records = cursor.fetchall()
            total = len(records)
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
        ,'total': total
        ,'key_word':key_word
    }



    return render(req, 'index.html', dados)


