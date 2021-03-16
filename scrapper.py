import requests
import json
from dumper import Dumper

class Scrapper:

    def __init__(self):
        self._config = self._get_config()

    def _get_config(self):
        with open('config.json', 'r') as outfile:
            return json.load(outfile)


    def _change_request_size(self, size):
        self._config['request']['size'] = size

    def _change_request_keyword(self, new_word):
        self._config['request']['query']['function_score']['query']['bool']['should'][0]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['should'][1]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['should'][2]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['filter'][0]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['should'][3]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['filter'][0]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][0]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][3]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][1]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][2]['query_string']['query'] = new_word


    def scrap(self, size, keyword):
        self._change_request_size(size)
        self._change_request_keyword(keyword)

        request_result = self._request_result()

        law_suit_data = self._extract_law_suit_data(request_result)

        self._dump_law_suit(law_suit_data)

    def _dump_law_suit(self, law_suit_data):
        insert_lawsuit_query = '''
                    insert into tb_jurisprudencia
                        (datacad, decisao, ementa, data_publicacao,
                        tema, tese, data_julgamento, classe_processual,
                        doutrina, relator)
                     output
                        inserted.id
                    values
                        (getdate(), ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
        insert_partes_query = '''
            insert into tb_partes (datacad, tipo, nome, id_tb_jurisprudencia)
                    values
                    (getdate(), ?, ?, ?)
        '''

        dumper_instance = Dumper()

        for law_suit in law_suit_data:

            insert_lawsuit_tuple = (
                law_suit['decisao'],
                law_suit['ementa'],
                law_suit['data_publicacao'],
                law_suit['tema'],
                law_suit['tese'],
                law_suit['data_julgamento'],
                law_suit['classe_processual'],
                law_suit['doutrina'],
                law_suit['relator'],
            )
            partes = law_suit['partes']

            inserted_id = dumper_instance.execute(insert_lawsuit_query, insert_lawsuit_tuple) \
                .fetchone() \
                .id

            insert_partes_params = [(parte['tipo'], parte['nome'], inserted_id) for parte in partes]
            dumper_instance.executemany(insert_partes_query, insert_partes_params)


    def _extract_law_suit_data(self, request_result):

        law_suit_data = []
        for raw_lawsuit in request_result['result']['hits']['hits']:
            decisao = raw_lawsuit['_source']['acordao_ata']

            ementa = raw_lawsuit['_source']['documental_legislacao_citada_texto']
            if (isinstance(ementa, list)):
                ementa = ''.join(ementa)
            elif (ementa is None):
                ementa = ''

            data_publicacao = raw_lawsuit['_source']['publicacao_data']
            tema = raw_lawsuit['_source']['documental_tese_tema_texto']
            tese = raw_lawsuit['_source']['documental_tese_texto']
            data_julgamento = raw_lawsuit['_source']['julgamento_data']
            classe_processual = raw_lawsuit['_source']['processo_classe_processual_unificada_extenso']
            doutrina = raw_lawsuit['_source']['documental_doutrina_texto']

            relator = raw_lawsuit['_source']['ministro_facet']
            if (isinstance(relator, list)):
                relator = ''.join(relator)
            elif (ementa is None):
                relator = ''

            partes_txt = raw_lawsuit['_source']['partes_lista_texto']
            partes_list = partes_txt.split('\n')
            partes = []
            for parte in partes_list:
                parte = parte.split(':')
                tipo = parte[0].strip()
                nome = parte[1].strip()
                partes.append({'tipo': tipo, 'nome': nome})

            law_suit = {
                'decisao': decisao,
                'ementa': ementa,
                'data_publicacao': data_publicacao,
                'tema': tema,
                'tese': tese,
                'data_julgamento': data_julgamento,
                'classe_processual': classe_processual,
                'doutrina': doutrina,
                'relator': relator,
                'partes': partes
            }

            law_suit_data.append(law_suit)

        return law_suit_data

    def _request_result(self):
        url = self._config['url']
        pay_load = self._config['request']
        pay_load = json.dumps(pay_load)
        response = requests.post(url, pay_load, verify=False)
        response = json.loads(response.text)
        return response



if __name__ == '__main__':
    dumper_instance = Dumper()
    scrap = Scrapper()
    scrap.scrap(10, 'carros')







