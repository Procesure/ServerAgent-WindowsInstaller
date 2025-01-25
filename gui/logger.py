import logging

from PyQt5.QtWidgets import QTextEdit


class GUILogger:

    def __init__(self, gui_log_output: QTextEdit):

        self.setup()
        self.gui_log_output = gui_log_output

    @staticmethod
    def setup():

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=r'C:\ProgramData\Procesure\installer-manager.log',
            filemode='a'
        )

    def log(self, message: str, level="info"):

        self.gui_log_output.append(message)

        if level == 'info':
            logging.info(message)
        elif level == 'error':
            logging.error(message)
        elif level == 'debug':
            logging.debug(message)
        else:
            logging.warning(message)
