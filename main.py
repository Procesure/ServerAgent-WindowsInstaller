import os
import sys
import subprocess
import platform
from pathlib import Path

def get_windows_version():
    """Detect Windows version and return version info."""
    try:
        output = subprocess.check_output(
            ["powershell", "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object Caption"],
            text=True
        )

        if "Windows 10" in output:
            return "Windows10"
        elif "Windows 11" in output:
            return "Windows11"
        elif "Windows Server 2016" in output:
            return "WindowsServer2016"
        else:
            raise ValueError(f"Unsupported Windows version detected: {output}")
    except subprocess.CalledProcessError as e:
        print(f"Error detecting Windows version: {e}")
        sys.exit(1)

def check_admin_privileges():
    """Check if the script is running with administrator privileges."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        print("Error checking admin privileges")
        return False

class WindowsServer2016Setup:
    @staticmethod
    def install_openssh():
        try:
            # Set the required protocol for downloads (TLS 1.2)
            subprocess.run(
                ["powershell", "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12"],
                check=True
            )

            # Create OpenSSH installation folder and download the OpenSSH zip
            subprocess.run(
                ["powershell", "mkdir c:\\openssh-install; cd c:\\openssh-install"],
                check=True
            )
            subprocess.run(
                [
                    "powershell",
                    "Invoke-WebRequest -Uri 'https://github.com/PowerShell/Win32-OpenSSH/releases/download/V8.6.0.0p1-Beta/OpenSSH-Win64.zip' -OutFile .\\openssh.zip"
                ],
                check=True
            )
            subprocess.run(
                ["powershell", "Expand-Archive .\\openssh.zip -DestinationPath .\\openssh\\"],
                check=True
            )
            subprocess.run(
                ["powershell", "cd .\\openssh\\OpenSSH-Win64\\"],
                check=True
            )

            # Add OpenSSH to PATH
            subprocess.run(
                ["powershell", "setx PATH '$env:path;c:\\openssh-install\\openssh\\OpenSSH-Win64\\' -m"],
                check=True
            )

            # Install SSH service
            subprocess.run(
                ["powershell", "powershell.exe -ExecutionPolicy Bypass -File install-sshd.ps1"],
                check=True
            )

            # Allow inbound SSH traffic through the firewall
            subprocess.run(
                [
                    "powershell",
                    "New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22"
                ],
                check=True
            )

            # Start SSH service
            subprocess.run(
                ["powershell", "net start sshd"],
                check=True
            )

            # Set SSH service to start automatically on system restart
            subprocess.run(
                ["powershell", "Set-Service sshd -StartupType Automatic"],
                check=True
            )

            print("OpenSSH installed and configured successfully on Windows Server 2016.")

        except subprocess.CalledProcessError as e:
            print(f"Failed to install OpenSSH on Windows Server 2016: {e}")
            raise

    @staticmethod
    def enable_rdp():
        try:
            print("Enabling RDP for Windows Server 2016...")
            commands = [
                ["powershell", "-Command", "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0"],
                ["powershell", "-Command", "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp' -Name 'UserAuthentication' -Value 1"]
            ]

            for cmd in commands:
                subprocess.run(cmd, check=True)

            print("RDP enabled successfully on Windows Server 2016")

        except subprocess.CalledProcessError as e:
            print(f"Error enabling RDP on Windows Server 2016: {e}")
            raise

def download_ngrok():
    """Download and install ngrok on Windows."""
    ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-windows-amd64.zip"
    ngrok_zip = "ngrok.zip"
    ngrok_dir = r"C:\Program Files\Procesure"

    try:
        # Ensure ngrok directory exists
        Path(ngrok_dir).mkdir(parents=True, exist_ok=True)

        # Download ngrok
        print("Downloading procesure agent...")
        subprocess.run(["curl", "-Lo", ngrok_zip, ngrok_url], check=True)

        # Extract ngrok
        subprocess.run(["tar", "-xf", ngrok_zip, "-C", ngrok_dir], check=True)

        # Remove zip file
        os.remove(ngrok_zip)

        ngrok_exe_path = os.path.join(ngrok_dir, "ngrok.exe")

        # Verify ngrok is installed
        if not os.path.exists(ngrok_exe_path):
            raise FileNotFoundError("ngrok.exe not found after extraction")

        print(f"Procesure agent installed in {ngrok_dir}")
        return ngrok_exe_path

    except Exception as e:
        print(f"Error downloading ngrok: {e}")
        sys.exit(1)

def setup_ngrok_service(ngrok_path):
    """Set up ngrok as a Windows service using the specified configuration file."""
    try:
        # Command to install ngrok service with the given configuration file
        config_path = r"C:\Program Files\Procesure\agent.yml"
        service_command = [ngrok_path, "service", "install", "--config", config_path]

        # Run the ngrok service installation command
        subprocess.run(service_command, check=True)

        print("ngrok service has been installed and configured.")

    except subprocess.CalledProcessError as e:
        print(f"Error setting up ngrok service: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def main():
    if not check_admin_privileges():
        print("Script must be run with administrator privileges")
        sys.exit(1)

    # Detect Windows version
    windows_version = get_windows_version()

    # Create setup instance based on Windows version
    setup_classes = {
        "Windows10": Windows10Setup,
        "Windows11": Windows11Setup,
        "WindowsServer2016": WindowsServer2016Setup
    }

    if windows_version not in setup_classes:
        print(f"Unsupported Windows version: {windows_version}")
        sys.exit(1)

    setup_class = setup_classes[windows_version]

    try:
        # Install OpenSSH
        setup_class.install_openssh()

        # Enable RDP
        setup_class.enable_rdp()

        # Download and setup ngrok
        ngrok_path = download_ngrok()
        setup_ngrok_service(ngrok_path)

        print(f"Setup complete for {windows_version}. Ngrok is running as a service.")

    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
