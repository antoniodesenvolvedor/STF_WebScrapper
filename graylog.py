import logging
from djehouty.libgelf.handlers import GELFTCPSocketHandler

class Graylog:

    def log(self, mensagem):
        gelf_logger = logging.getLogger('djehouty-gelf')
        gelf_logger.setLevel(logging.DEBUG)
        gelf_logger.addHandler(GELFTCPSocketHandler(
            host="host.docker.internal",
            port=12201,
            static_fields={"app": 'STF Scrapper'},
            null_character=True,
        ))

        mensagem = 'error message:' + str(mensagem)

        gelf_logger.info(mensagem)
        print('Log enviado')

if __name__ == '__main__':
    gray_log = Graylog()
    gray_log.log('error message')

