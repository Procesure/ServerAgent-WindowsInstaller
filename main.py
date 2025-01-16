import sys
from PyQt5.QtWidgets import QApplication
from gui import ModernConfigGUI
from setup_classes import Windows10Setup, Windows11Setup, WindowsServer2016Setup
from utils import (
    check_admin_privileges,
    get_windows_version,
    create_ngrok_config,
    download_ngrok,
    setup_ngrok_service,
    setup_rdp_loopback
)


def main():
    if not check_admin_privileges():
        print("This script requires administrator privileges. Please run as administrator.")
        sys.exit(1)

    windows_version = get_windows_version()

    # Create GUI
    app = QApplication(sys.argv)
    gui = ModernConfigGUI()

    def start_installation(auth_token, ip_address, install_path, ssh_keys_path):
        # Redirect stdout to the GUI log for installation process
        sys.stdout = gui.get_log_handler()
        
        print(f"Detected Windows version: {windows_version}")
        print("Starting installation process...")

        try:
            # Create ngrok configuration
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

            # Install OpenSSH
            setup_class.install_openssh(ssh_keys_path)

            # Enable RDP
            setup_class.enable_rdp()

            # Download and setup ngrok
            ngrok_path = download_ngrok(install_path)
            setup_ngrok_service(ngrok_path)
            setup_rdp_loopback()

            print(f"Setup complete for {windows_version}. Ngrok is running as a service.")

        except Exception as e:
            print(f"Setup failed: {e}")
            sys.exit(1)

    # Connect the signal to start installation
    gui.config_ready.connect(lambda auth, ip, path: gui.start_installation_process(
        lambda a, i, p, ssh_path: start_installation(a, i, p, ssh_path)
    ))
    
    # Show the GUI
    gui.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
