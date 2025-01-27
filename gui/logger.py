import logging
from pathlib import Path
from PyQt5.QtWidgets import QTextEdit


class GUILogger:

    log_file_path: Path = Path(r'C:\ProgramData\Procesure\installer-manager.log')

    def __init__(self):
        self.gui_log_output = None
        self.logger = self.setup()

    @staticmethod
    def setup():

        logger = logging.getLogger('GUILogger')
        logger.setLevel(logging.DEBUG)
        GUILogger.log_file_path.parent.mkdir(exist_ok=True)

        if not logger.handlers:
            file_handler = logging.FileHandler(GUILogger.log_file_path, mode='a')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def set_gui_log_output(self, gui_log_output: QTextEdit) -> None:
        self.gui_log_output = gui_log_output

    def log(self, message: str, level="info"):

        if self.gui_log_output:
            self.gui_log_output.append(message)

        {
            'info': self.logger.info,
            'error': self.logger.error,
            'debug': self.logger.debug,
            'warning': self.logger.warning
        }[level](message)

gui_logger = GUILogger()