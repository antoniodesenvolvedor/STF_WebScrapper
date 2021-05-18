import pyodbc
import json
import traceback
from graylog import Graylog

class Dumper:
    def __init__(self):
        self._connect()


    def _connect(self):
        self._database_config = self._get_config()['database']

        # driver = ''
        # if platform == "linux" or platform == "linux2":
        #     driver = '{FreeTDS}'
        # elif platform == "win32":
        driver = '{ODBC Driver 17 for SQL Server}'

        print(driver)

        user = self._database_config['user']
        password = self._database_config['password']
        server = self._database_config['server']
        database = self._database_config['database']

        connection_string = \
            f'Driver={driver};' \
            f'Server={server};' \
            f'Database={database};' \
            f'UID={user};' \
            f'PWD={password}'

        self._connection = pyodbc.connect(connection_string, autocommit=False)
        self._cursor = self._connection.cursor()


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

    def _commit(self):
        self._connection.commit()

    def _close_cnn(self):
        self._connection.close()


    def dump_total(self, total, idbusca):
        print(f'dump total {total}')
        query = '''
            update STF.TB_BUSCA_JURISPRUDENCIA set total = ? where idbusca = ?
             '''
        try:
            self.execute(query, (total, idbusca))
            self._commit()
        except Exception:
            print('Fechando conexao erro:' + traceback.format_exc())
            self._close_cnn()
            self._connect()

    def dump_law_suit(self, law_suit_data, idbusca):
        insert_lawsuit_query = '''
            insert into STF.TB_RETORNO_JURISPRUDENCIA
                (IDBUSCA, datacad, decisao, ementa, data_publicacao,
                tema, tese, data_julgamento, classe_processual,
                doutrina, relator,legislacao)
             output
                inserted.idretorno
            values
                (?, getdate(), ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        '''
        insert_partes_query = '''
            insert into STF.TB_RETORNO_JURISPRUDENCIA_PARTES (datacad, tipo, nome, id_tb_jurisprudencia)
                    values
                    (getdate(), ?, ?, ?)
        '''

        print(len(law_suit_data))
        for law_suit in law_suit_data:

            insert_lawsuit_tuple = (
                idbusca,
                law_suit['decisao'],
                law_suit['ementa'],
                law_suit['data_publicacao'],
                law_suit['tema'],
                law_suit['tese'],
                law_suit['data_julgamento'],
                law_suit['classe_processual'],
                law_suit['doutrina'],
                law_suit['relator'],
                law_suit['legislacao'],
            )
            partes = law_suit['partes']


            try:
                idretorno = self.execute(insert_lawsuit_query, insert_lawsuit_tuple) \
                    .fetchone() \
                    .idretorno

                insert_partes_params = [(parte['tipo'], parte['nome'], idretorno) for parte in partes]
                self.executemany(insert_partes_query, insert_partes_params)

                self._commit()
            except Exception:

                print('Fechando conexao erro:' + traceback.format_exc())
                self._close_cnn()
                self._connect()


    def finalizar_sucesso(self, idlinha, mensagem):
        self.finalizar_linha(idlinha, 4, mensagem)

    def finalizar_erro(self, idlinha, mensagem):
        self.finalizar_linha(idlinha, 3, mensagem)


    def finalizar_linha(self, idlinha, status, mensagem):
        query = '''
        update
            linha
        set
            idstatus = ?
            ,DATA_FIM_PROCESSAMENTO = getdate()
            , historico = isnull(historico,'') + ' || ' + ?
        from
            TB_LOTE_LINHA linha
        where
            linha.idlinha = ?
        '''
        try:
            self.execute(query, (status, mensagem, idlinha))
            self._commit()
        except Exception as e:
            print('Fechando conexao erro:' + str(e))
            self._close_cnn()
            self._connect()


    def get_next_case(self):
        query = '''     
            UPDATE
                LINHA
            SET
                IDSTATUS = 2,
                DATA_INICIO_PROCESSAMENTO = getdate(),
                historico = isnull(historico,'') + ' || Inicio do processamento em: ' +
                    convert(varchar,getdate(),103) + ' ' + convert(varchar,getdate(),108)
            OUTPUT
                INSERTED.idlinha
				,BUSCA.palavra_chave
				,busca.idbusca
			FROM
				TB_LOTE LOTE WITH(NOLOCK)
				INNER JOIN TB_LOTE_LINHA LINHA WITH(UPDLOCK) ON LOTE.IDLOTE = LINHA.idlote
				INNER JOIN STF.TB_BUSCA_JURISPRUDENCIA BUSCA WITH(NOLOCK) ON BUSCA.IDLINHA = LINHA.IDLINHA
            WHERE
                LINHA.IDSTATUS = 1
                AND LINHA.IDLINHA IN (
					select
						top 1 LINHA.IDLINHA
					FROM
						TB_LOTE LOTE WITH(NOLOCK)
						INNER JOIN TB_LOTE_LINHA LINHA WITH(UPDLOCK) ON LOTE.IDLOTE = LINHA.idlote
						INNER JOIN STF.TB_BUSCA_JURISPRUDENCIA BUSCA WITH(NOLOCK) ON BUSCA.IDLINHA = LINHA.IDLINHA
					WHERE
						LINHA.IDSTATUS = 1
					ORDER BY LINHA.IDLINHA ASC
				)
        '''
        try:
            result = self.execute(query).fetchone()
            proximo_registro = {}
            if(result):
                proximo_registro['idlinha'] = result[0]
                proximo_registro['palavra_chave'] = result[1]
                proximo_registro['idbusca'] = result[2]
            self._commit()
            return proximo_registro
        except Exception as e:
            print('Fechando conexao erro:' + str(e))
            self._close_cnn()
            self._connect()




