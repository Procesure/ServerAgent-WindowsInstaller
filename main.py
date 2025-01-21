from installers.winserver2016 import WinServer2016Installer

if __name__ == "__main__":

    installer = WinServer2016Installer()
    installer.start(installer.handle_installations)