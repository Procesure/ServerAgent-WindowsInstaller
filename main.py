import sys
from PyQt6.QtWidgets import QApplication
from gui import ModernConfigGUI
from setup_classes import Windows10Setup, Windows11Setup, WindowsServer2016Setup
from utils import (
    check_admin_privileges,
    get_windows_version,
    create_ngrok_config,
    download_ngrok,
    setup_ngrok_service
)


def main():
    # Create GUI and get configuration
    app = QApplication(sys.argv)
    gui = ModernConfigGUI()
    
    # Redirect stdout to the GUI log
    sys.stdout = gui.get_log_handler()
    
    if not check_admin_privileges():
        print("This script requires administrator privileges. Please run as administrator.")
        sys.exit(1)

    windows_version = get_windows_version()
    print(f"Detected Windows version: {windows_version}")

    auth_token, ip_address, install_path = gui.get_config()

    if not auth_token or not ip_address:
        print("Configuration cancelled or incomplete.")
        sys.exit(1)

    create_ngrok_config(authtoken=auth_token, ssh_domain=ip_address, install_path=install_path)

    # Initialize the appropriate setup class based on Windows version
    setup_classes = {
        "Windows11": Windows11Setup,
        "Windows10": Windows10Setup,
        "WindowsServer2016": WindowsServer2016Setup,
    }

    setup_class = setup_classes.get(windows_version)
    if not setup_class:
        print(f"Unsupported Windows version: {windows_version}")
        sys.exit(1)

    try:
        # Install OpenSSH
        setup_class.install_openssh()

        # Enable RDP
        setup_class.enable_rdp()

        # Download and setup ngrok
        ngrok_path = download_ngrok(install_path)
        setup_ngrok_service(ngrok_path)

        print(f"Setup complete for {windows_version}. Ngrok is running as a service.")

    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
