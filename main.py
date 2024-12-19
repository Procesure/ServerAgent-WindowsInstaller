import os
import sys
import subprocess
from pathlib import Path


def check_admin_privileges():

    """Check if the script is running with administrator privileges."""

    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        print("Error checking admin privileges")
        return False


def download_and_install_open_ssh():

    """
    Installs OpenSSH server on Windows if it's not already installed.
    This function uses PowerShell commands to ensure OpenSSH is available.

    """

    try:
        # Check if OpenSSH is already installed
        check_command = [
            "powershell",
            "-Command",
            "Get-WindowsCapability -Online | Where-Object { $_.Name -like '*OpenSSH*' }"
        ]

        process = subprocess.run(
            check_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "Installed" in process.stdout:
            print("OpenSSH is already installed on the system.")
            return

        # Install OpenSSH client and server
        print("OpenSSH not found. Installing OpenSSH client and server...")
        install_command = [
            "powershell",
            "-Command",
            "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
        ]
        subprocess.run(install_command, check=True)

        # Start and enable OpenSSH server service
        print("Starting and enabling OpenSSH server service...")
        start_service_command = [
            "powershell",
            "-Command",
            "Start-Service sshd; Set-Service -Name sshd -StartupType Automatic"
        ]
        subprocess.run(start_service_command, check=True)

        print("OpenSSH installation and setup complete.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install or configure OpenSSH: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during OpenSSH installation: {e}")


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


def enable_ssh_rdp():

    """Enable SSH and RDP on Windows."""

    try:
        print("Enabling SSH and RDP...")

        # Enable SSH service
        subprocess.run([
            "powershell",
            "-Command",
            "Set-Service -Name 'sshd' -StartupType Automatic"
        ], check=True)

        subprocess.run([
            "powershell",
            "-Command",
            "Start-Service 'sshd'"
        ], check=True)

        # Enable Remote Desktop
        subprocess.run([
            "powershell",
            "-Command",
            "Set-NetFirewallRule -DisplayGroup 'Remote Desktop' -Enabled True"
        ], check=True)

        print("SSH and RDP enabled successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error enabling SSH/RDP: {e}")
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
    # Check for admin privileges
    if not check_admin_privileges():
        print("Script must be run with administrator privileges")
        sys.exit(1)

    download_and_install_open_ssh()

    # Step 1: Download and install ngrok
    ngrok_path = download_ngrok()

    # Step 2: Enable SSH and RDP
    enable_ssh_rdp()

    # Step 3: Set up ngrok as a service
    setup_ngrok_service(ngrok_path)

    print("Setup complete. Ngrok is running as a service.")


if __name__ == "__main__":
    main()
