import logging
from djehouty.libgelf.handlers import GELFTCPSocketHandler

class Graylog:

    def log(self, mensagem):
        gelf_logger = logging.getLogger('djehouty-gelf')
        gelf_logger.setLevel(logging.DEBUG)
        gelf_logger.addHandler(GELFTCPSocketHandler(
            host="127.0.0.1",
            port=12201,
            static_fields={"app": 'STF Scrapper'},
            null_character=True,
        ))

        gelf_logger.info('error message' + mensagem)
        print('Log enviado')

if __name__ == '__main__':
    gray_log = Graylog()
    gray_log.log('error message')

