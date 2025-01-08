import os
import sys
import subprocess
import requests
import yaml
from pathlib import Path
import zipfile


def get_windows_version():
    """Detect Windows version and return version info."""
    try:
        output = subprocess.check_output(
            [
                "powershell",
                "Get-CimInstance -ClassName Win32_OperatingSystem | Select-Object Caption",
            ],
            text=True,
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


def download_ngrok(install_path):
    """Download and install ngrok on Windows."""
    ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-windows-amd64.zip"
    ngrok_zip = "ngrok.zip"

    try:
        # Ensure ngrok directory exists
        Path(install_path).mkdir(parents=True, exist_ok=True)

        # Download ngrok
        print("Downloading procesure agent...")
        response = requests.get(ngrok_url)
        response.raise_for_status()  # Raise an error for bad HTTP status
        with open(ngrok_zip, "wb") as f:
            f.write(response.content)

        # Extract ngrok
        print("Extracting ngrok...")
        with zipfile.ZipFile(ngrok_zip, "r") as zip_ref:
            zip_ref.extractall(install_path)

        # Delete the zip file
        print("Cleaning up temporary files...")
        os.remove(ngrok_zip)

        print("Ngrok setup completed successfully.")

        ngrok_exe_path = os.path.join(install_path, "ngrok.exe")
        return ngrok_exe_path

    except Exception as e:
        # Clean up zip file if it exists, even if there was an error
        if os.path.exists(ngrok_zip):
            try:
                os.remove(ngrok_zip)
            except Exception:
                pass  # Ignore cleanup errors
        print(f"Error downloading ngrok: {e}")
        sys.exit(1)


def setup_ngrok_service(ngrok_path):
    """Set up ngrok as a Windows service using the specified configuration file."""
    try:
        # Command to install ngrok service with the given configuration file
        config_path = os.path.join(os.path.dirname(ngrok_path), "agent.yml")
        service_command = [ngrok_path, "service", "install", "--config", config_path]
        start_command = [ngrok_path, "service", "start"]

        # Run the ngrok service installation command
        subprocess.run(service_command, check=True)
        subprocess.run(start_command, check=True)

        print("ngrok service has been installed, started and configured.")

    except subprocess.CalledProcessError as e:
        print(f"Error setting up ngrok service: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def create_ngrok_config(authtoken, ssh_domain, install_path):
    """Create ngrok configuration file."""
    config = {
        "version": "3",
        "agent": {
            "authtoken": authtoken
        },
        "tunnels": {
            "ssh": {
                "proto": "tcp",
                "addr": 22,
                "remote_addr": ssh_domain
            }
        }
    }

    try:
        # Create directory if it doesn't exist
        os.makedirs(install_path, exist_ok=True)
        
        # Use install_path for config file
        config_path = os.path.join(install_path, "agent.yml")
        
        # Use PyYAML to write the config file in YAML format
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False)
        print(f"ngrok configuration saved at {config_path}")
        return config_path
    except IOError as e:
        print(f"Error writing ngrok configuration: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error creating ngrok configuration: {e}")
        raise 