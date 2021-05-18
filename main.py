from scrapper import Scrapper
from dumper import Dumper
from time import sleep
import math
import traceback
from graylog import Graylog

if __name__ == '__main__':
    # while True:
    #     print('Aguardando 10 segundos')
    #     sleep(10)
    dumper_instance = Dumper()
    stf_scrapper = Scrapper()

    request_size = stf_scrapper.get_request_size()

    while True:
        try:
            next_case = dumper_instance.get_next_case()
            if next_case:
                print(f"carga encontrada idlinha {next_case['idlinha']}")
            if not next_case:
                print('Nenhuma carga encontrada')
                sleep(15)
                continue

            stf_scrapper.change_request_keyword(next_case['palavra_chave'])
            stf_scrapper.change_pagination(0)


            law_suit_data, total = stf_scrapper.scrap()
            dumper_instance.dump_law_suit(law_suit_data, next_case['idbusca'])

            total_iteration = math.ceil(total / request_size)
            print(total_iteration)
            print(total)
            dumper_instance.dump_total(total, next_case['idbusca'])

            for i in range(1, total_iteration):
                stf_scrapper.change_pagination(request_size * i)
                sleep(1)
                law_suit_data = stf_scrapper.scrap()[0]
                print(f'Dumping request {i + 1}')
                dumper_instance.dump_law_suit(law_suit_data, next_case['idbusca'])

            print(f"Finalizando linha {next_case['idlinha']}")
            dumper_instance.finalizar_sucesso(next_case['idlinha'], 'Finalizado com sucesso')
        except Exception:
            gray_log = Graylog()
            mensagem = traceback.format_exc()
            gray_log.log(mensagem)
            dumper_instance.finalizar_erro(next_case['idlinha'], mensagem)







