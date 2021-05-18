import requests
import json
from dumper import Dumper
import math
import time

class Scrapper:

    def __init__(self):
        self._config = self._get_config()

    def _get_config(self):
        with open('config.json', 'r') as outfile:
            return json.load(outfile)


    def change_request_size(self, size):
        self._config['request']['size'] = size

    def get_request_size(self):
        return int(self._config['request']['size'])

    def change_pagination(self, page):
        self._config['request']['from'] = page

    def change_request_keyword(self, new_word):
        self._config['request']['query']['function_score']['query']['bool']['should'][0]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['should'][1]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['should'][2]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['should'][3]['query_string']['query'] = new_word
        self._config['request']['query']['function_score']['query']['bool']['filter'][0]['query_string']['query'] = new_word

        self._config['request']['highlight']['highlight_query']['bool']['filter'][0]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][0]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][3]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][1]['query_string']['query'] = new_word
        self._config['request']['highlight']['highlight_query']['bool']['should'][2]['query_string']['query'] = new_word



    def scrap(self):

        url = self._config['url']
        payload = self._config['request']
        headers = self._config['headers']
        print('Making request...')
        request = self._do_post(url, payload, headers)
        print('Extracting information...')

        law_suit_data, total = self._extract_law_suit_data(request)


        return [law_suit_data, total]




    def _extract_law_suit_data(self, request_result):

        law_suit_data = []
        total = request_result['result']['hits']['total']['value']
        for raw_lawsuit in request_result['result']['hits']['hits']:
            decisao = raw_lawsuit['_source']['acordao_ata']


            ementa = raw_lawsuit['_source']['ementa_texto']

            legislacao = raw_lawsuit['_source']['documental_legislacao_citada_texto']
            if (isinstance(legislacao, list)):
                legislacao = ''.join(legislacao)
            elif (legislacao is None):
                legislacao = ''

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

            if partes_txt is not None:
                partes_list = partes_txt.split('\n')

            partes = []
            for parte in partes_list:
                parte = parte.split(':')

                tipo = None
                nome = None
                if (len(parte) >= 2):
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
                'partes': partes,
                'legislacao' : legislacao
            }

            law_suit_data.append(law_suit)

        return [law_suit_data, total]


    def _do_post(self, url, payload, headers) -> json:
        payload = json.dumps(payload)
        response = requests.post(url, payload, verify=False, headers=headers)
        print(response)
        response = json.loads(response.text)
        return response




if __name__ == '__main__':
    pass







