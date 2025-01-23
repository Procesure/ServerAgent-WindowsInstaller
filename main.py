from installers.winserver2016 import WinServer2016Installer
from managers.open_ssh.manager import WinServer2016OpenSSHManager, SSHConfig

if __name__ == "__main__":

    # installer = WinServer2016Installer()
    # installer.start(installer.handle_installations)

    manager = WinServer2016OpenSSHManager(config=SSHConfig(username="123", public_key="123"))
    manager.handle_installation()
