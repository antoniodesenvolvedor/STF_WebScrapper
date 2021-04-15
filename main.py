from scrapper import Scrapper
from dumper import Dumper
from time import sleep
import math
import traceback

if __name__ == '__main__':
    # while True:
    #     print('Aguardando 10 segundos')
    #     sleep(10)
    dumper_instance = Dumper()
    stf_scrapper = Scrapper()

    request_size = stf_scrapper.get_request_size()

    while True:
        next_case = dumper_instance.get_next_case()
        if not next_case:
            print('Nenhuma carga encontrada')
            sleep(15)
            continue
        try:
            stf_scrapper.change_request_keyword(next_case['palavra_chave'])

            law_suit_data, total = stf_scrapper.scrap()
            dumper_instance.dump_law_suit(law_suit_data, next_case['idbusca'])

            total_iteration = math.ceil(total / request_size)

            for i in range(1, total_iteration):
                stf_scrapper.change_pagination(request_size * i)
                sleep(1)
                law_suit_data = stf_scrapper.scrap()[0]
                print(f'Request {i + 1} done')
                dumper_instance.dump_law_suit(law_suit_data, next_case['idbusca'])

            print(f"Finalizando linha {next_case['idlinha']}")
            dumper_instance.finalizar_sucesso(next_case['idlinha'], 'Finalizado com sucesso')
        except Exception:
            mensagem = traceback.format_exc()
            dumper_instance.finalizar_erro(next_case['idlinha'], mensagem)







