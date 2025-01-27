import os
from dotenv import load_dotenv

from installers.winserver2016 import WinServer2016Installer
from testes import installation_config

load_dotenv()

if __name__ == "__main__":

    installer = WinServer2016Installer()
    installer.handle_installations(installation_config)
    # installer.start(installer.handle_installations)

