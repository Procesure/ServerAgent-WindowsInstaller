import os
import sys
import platform
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


def run_powershell_command(command):
    """Runs a PowerShell command and returns the output."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr)
        sys.exit(1)


def get_windows_version():
    """Retrieve the Windows version and build number."""
    version = platform.version()
    release = platform.release()
    return release, version


def install_openssh():
    """Install OpenSSH based on Windows version."""
    release, version = get_windows_version()
    print(f"Detected Windows Version: Release: {release}, Version: {version}")

    if int(release) >= 10:  # Windows 10 and Server 2016+
        print("Installing OpenSSH using Add-WindowsCapability...")
        commands = [
            "Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0",
            "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0",
            "Start-Service sshd",
            "Set-Service -Name sshd -StartupType 'Automatic'",
            "if (!(Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue)) { "
            "New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True "
            "-Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 }"
        ]
    else:
        print("Manual installation required for this Windows version.")
        print("Please download OpenSSH from the official repository.")
        sys.exit(1)

    for command in commands:
        print(f"Running: {command}")
        run_powershell_command(command)
    print("OpenSSH installation and configuration completed.")


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

    # Step 1: Install OpenSSH based on Windows version
    install_openssh()

    # Step 2: Download and install ngrok
    ngrok_path = download_ngrok()

    # Step 3: Enable SSH and RDP
    enable_ssh_rdp()

    # Step 4: Set up ngrok as a service
    setup_ngrok_service(ngrok_path)

    print("Setup complete. Ngrok is running as a service.")


if __name__ == "__main__":
    main()
