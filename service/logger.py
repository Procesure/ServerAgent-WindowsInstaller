import logging
from pathlib import Path


class ServiceLogger:

    log_file_path: Path = Path(r"C:\ProgramData\Procesure\service.log")

    def __init__(self):
        self.logger = self.setup()

    @staticmethod
    def setup():

        logger = logging.getLogger('ServiceLogger')
        logger.setLevel(logging.DEBUG)
        ServiceLogger.log_file_path.parent.mkdir(exist_ok=True)

        if not logger.handlers:

            file_handler = logging.FileHandler(ServiceLogger.log_file_path, mode='a')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


    def log(self, message: str, level="info"):
        {
            'info': self.logger.info,
            'error': self.logger.error,
            'debug': self.logger.debug,
            'warning': self.logger.warning
        }[level](message)

svc_logger = ServiceLogger()