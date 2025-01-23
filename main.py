import os

from dotenv import load_dotenv

from installers.winserver2016 import WinServer2016Installer
from managers.open_ssh.manager import WinServer2016OpenSSHManager, SSHConfig

load_dotenv()

if __name__ == "__main__":

    # installer = WinServer2016Installer()
    # installer.start(installer.handle_installations)

    manager = WinServer2016OpenSSHManager(config=SSHConfig(username=os.getenv("SSH_USERNAME"), public_key=os.getenv("SSH_PUBLIC_KEY")))
    manager.handle_installation()
