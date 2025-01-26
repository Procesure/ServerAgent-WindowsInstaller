import logging
from pathlib import Path


class ServiceLogger:

    def __init__(self):
        self.setup()

    @staticmethod
    def setup():

        path = Path(r"C:\ProgramData\Procesure")
        path.mkdir(exist_ok=True, parents=True)

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=path,
            filemode='a'
        )

    @staticmethod
    def log(message: str, level="info"):

        if level == 'info':
            logging.info(message)
        elif level == 'error':
            logging.error(message)
        elif level == 'debug':
            logging.debug(message)
        else:
            logging.warning(message)

svc_logger = ServiceLogger()