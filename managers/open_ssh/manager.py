import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from .models import SSHConfig, StrictStr
from typing import List


class OpenSSHManager(ABC):

    program_data_ssh: Path = Path("C:\ProgramData\ssh")
    powershell: StrictStr = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

    def __init__(self, config: SSHConfig):
        self.config = config

    @abstractmethod
    def check_if_installed(self) -> bool:
        pass

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def add_open_ssh_to_path(self):
        pass

    @abstractmethod
    def configure_ssh_service(self):
        pass

    @abstractmethod
    def configure_firewall(self):
        pass

    @abstractmethod
    def configure_authorized_keys(self):
        pass

    @abstractmethod
    def setup_ssh_program_data(self):
        pass

    @abstractmethod
    def fix_host_file_permissions(self):
        pass

    @abstractmethod
    def update_sshd_config(self):
        pass

    def handle_installation(self):

        is_installed = self.check_if_installed()

        if not is_installed:
            self.install()
            
        self.config.open_ssh_installation_path = self.config.open_ssh_installation_path / "OpenSSH-Win64"

        self.add_open_ssh_to_path()
        self.setup_ssh_program_data()
        self.configure_firewall()
        self.configure_authorized_keys()
        self.update_sshd_config()
        self.configure_ssh_service()


class WinServer2016OpenSSHManager(OpenSSHManager):

    common_installation_paths: List[Path] = [
        Path("C:\Program Files\OpenSSH-Win64"),
        Path("C:\Windows\System32\OpenSSH"),
        Path("C:\Program Files (x86)\OpenSSH"),
    ]

    def __init__(self, config: SSHConfig):
        super().__init__(config)

    def search_openssh(self) -> Path | None:

        """Search for OpenSSH in common installation locations."""

        for path in self.common_installation_paths:

            sshd_path = os.path.join(path, "sshd.exe")
            if os.path.exists(sshd_path):
                return Path(sshd_path)

        return None

    def check_if_installed(self) -> bool:

        """Check if OpenSSH is already installed."""

        is_installed = bool(self.search_openssh())

        if is_installed:
            print("OpenSSH is already installed.")
        else:
            print("OpenSSH not found in the system.")

        return is_installed

    def install(self):

        """Install OpenSSH if it is not already installed."""

        print("Installing OpenSSH...")

        try:

            self.config.open_ssh_installation_path = self.config.open_ssh_installation_path
            self.config.open_ssh_installation_path.mkdir(parents=True, exist_ok=True)

            # Download OpenSSH
            subprocess.run(
                [
                    self.powershell,
                    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "
                    f"Invoke-WebRequest -Uri 'https://github.com/PowerShell/Win32-OpenSSH/releases/download/V8.6.0.0p1-Beta/OpenSSH-Win64.zip' "
                    f"-OutFile '{self.config.open_ssh_installation_path / 'openssh.zip'}'",
                ],
                check=True,
            )

            # Extract OpenSSH
            subprocess.run(
                [
                    self.powershell,
                    f"Expand-Archive -Path '{self.config.open_ssh_installation_path / 'openssh.zip'}' -DestinationPath '{self.config.open_ssh_installation_path}'",
                ],
                check=True,
            )

            # Delete the ZIP file after extraction
            zip_file_path = self.config.open_ssh_installation_path / "openssh.zip"
            if zip_file_path.exists():
                zip_file_path.unlink()

            self.add_open_ssh_to_path()
            print("OpenSSH installation completed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install OpenSSH: {e}")
            raise

    def add_open_ssh_to_path(self):

        """Add OpenSSH installation path to the system PATH."""

        try:

            subprocess.run(
                [
                    self.powershell,
                    f"[System.Environment]::SetEnvironmentVariable('PATH', $env:PATH + ';{self.config.open_ssh_installation_path}', 'Machine')"
                ],
                check=True,
            )
            print("OpenSSH installation path added to PATH using PowerShell.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to add OpenSSH to PATH: {e}")
            raise

    def setup_ssh_program_data(self):

        """Ensure the ProgramData\ssh folder exists and contains required files."""

        self.program_data_ssh.mkdir(parents=True, exist_ok=True)

        sshd_config_path = self.program_data_ssh / "sshd_config"

        if not sshd_config_path.exists():

            default_config_path = self.config.open_ssh_installation_path / "sshd_config_default"

            if default_config_path.exists():

                default_config_path.rename(sshd_config_path)
                print(f"Moved {default_config_path} to {sshd_config_path}")

            else:

                print("Default sshd_config not found. Creating a new one...")
                with sshd_config_path.open("w") as f:
                    f.write("# Default sshd_config generated by installer\n")

        self.create_host_keys()

    def create_host_keys(self):

        print("Generating all missing host keys...")

        try:
            subprocess.run(
                [
                    self.config.open_ssh_installation_path / "ssh-keygen.exe",
                    "-A",
                ],
                check=True,
            )
            print("Host keys generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate host keys: {e}")
            raise

    def configure_ssh_service(self):

        """Install and start the OpenSSH service."""

        try:

            install_script = self.config.open_ssh_installation_path / "install-sshd.ps1"

            print(f"Executing install-sshd.ps1 from {install_script}...")

            result = subprocess.run(
                [
                    self.powershell,
                    "-ExecutionPolicy", "Bypass",
                    "-File", str(install_script),
                ],
                check=True,
                text=True,
                capture_output=True,
                cwd=str(self.config.open_ssh_installation_path),  # Set working directory
                env={**os.environ, "PATH": f"{os.environ['PATH']};C:\\Windows\\System32"},
            )
            print(f"Script Output: {result.stdout}")
            print(f"Script Errors: {result.stderr}")

            self.fix_host_file_permissions()

            # Start the sshd service
            print("Starting sshd service...")

            result = subprocess.run(
                [self.powershell, "-Command", "net start sshd"],
                env={**os.environ, "PATH": f"{os.environ['PATH']};C:\\Windows\\System32"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            print("Command:", result.args)
            print("Exit Code:", result.returncode)
            print("Output:", result.stdout)
            print("Error:", result.stderr)

            # Set sshd service to start automatically
            print("Configuring sshd to start automatically...")

            subprocess.run(
                [self.powershell, "-Command", "Set-Service -Name sshd -StartupType Automatic"],
                check=True,
            )

            print("SSHD service configured successfully.")

        except subprocess.CalledProcessError as e:
            print(f"Failed to configure SSH service. Command: {e.cmd}\nExit Code: {e.returncode}")
            print(f"Output: {e.stdout}\nError: {e.stderr}")
            raise
        except Exception as e:
            print(f"Unexpected error configuring SSH service: {e}")
            raise

    def fix_host_file_permissions(self):

        fix_host_permissions_path = self.config.open_ssh_installation_path / "FixHostFilePermissions.ps1"

        try:

            subprocess.run(
                [
                    self.powershell,
                    "-NoProfile",
                    "-ExecutionPolicy", "Bypass",
                    "-Command",
                    f"& '{fix_host_permissions_path}' -Confirm:$false"
                ],
                check=True,
                capture_output=True,
                text=True
            )

            print("FixHostFilePermissions script executed successfully without prompting.")

        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e.stderr}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def configure_firewall(self):

        """Allow inbound SSH traffic through the firewall."""

        try:

            # Remove the existing rule if it exists
            subprocess.run(
                [
                    self.powershell,
                    "if (Get-NetFirewallRule -Name sshd -ErrorAction SilentlyContinue) { Remove-NetFirewallRule -Name sshd }"
                ],
                check=True,
            )

            print("Existing 'sshd' firewall rule removed.")

            # Add the firewall rule
            subprocess.run(
                [
                    self.powershell,
                    "New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22",
                ],
                check=True,
            )

            print("Firewall rule 'sshd' created successfully.")

        except subprocess.CalledProcessError as e:
            print(f"Failed to configure firewall for SSH. Error: {e.stderr}")
            raise
        except Exception as e:
            print(f"Unexpected error configuring firewall: {e}")
            raise

    def configure_authorized_keys(self):

        try:

            user_ssh_path = Path(f"C:/Users/{self.config.username}/.ssh")
            user_ssh_path.mkdir(parents=True, exist_ok=True)

            authorized_keys_path = user_ssh_path / "procesure_authorized_keys"

            if not authorized_keys_path.exists():
                authorized_keys_path.touch()

            # Append the public key if it's not already in the file
            with authorized_keys_path.open("a+") as f:
                f.seek(0)
                existing_keys = f.read()
                if self.config.public_key not in existing_keys:
                    f.write(f"{self.config.public_key}\n")

            # Set permissions for the folder and file (optional)
            subprocess.run(
                [
                    "icacls",
                    str(user_ssh_path),
                    "/inheritance:r",
                    "/grant:r",
                    f"{self.config.username}:F",
                ],
                check=True,
            )

            print(f"Configured authorized_keys for {self.config.username}.")
        except Exception as e:
            print(f"Failed to configure authorized_keys for {self.config.username}: {e}")
            raise

    def update_sshd_config(self):

        """Add a Match User directive to sshd_config with proper spacing and indentation."""

        try:

            sshd_config_path = self.program_data_ssh / "sshd_config"

            # Ensure sshd_config exists, or create a default one
            if not sshd_config_path.exists():
                print(f"sshd_config not found at {sshd_config_path}, creating a new one...")
                sshd_config_path.parent.mkdir(parents=True, exist_ok=True)
                with sshd_config_path.open("w") as f:
                    f.write("# Default sshd_config generated by installer\n")

            # Backup the current sshd_config
            sshd_config_backup = sshd_config_path.with_suffix(".bak")
            if not sshd_config_backup.exists():
                sshd_config_backup.write_text(sshd_config_path.read_text())
                print(f"Backed up sshd_config to {sshd_config_backup}")
            else:
                print(f"Backup already exists at {sshd_config_backup}, skipping backup.")

            # Read the current sshd_config
            with sshd_config_path.open("r") as f:
                config_lines = f.readlines()

            # Prepare the Match User directive
            match_directive = f"Match User {self.config.username}\n"
            authorized_keys_path = Path(f"C:/Users/{self.config.username}/.ssh/procesure_authorized_keys")
            match_block = [
                match_directive,
                f"       AuthorizedKeysFile {authorized_keys_path}\n",
            ]

            # Check if a Match User directive already exists for the user
            if any(line.strip() == match_directive.strip() for line in config_lines):
                print(f"Match User directive for {self.config.username} already exists in sshd_config.")
                return

            # Find where to insert the Match User directive
            insert_index = next(
                (i for i, line in enumerate(config_lines) if line.strip().startswith("Match ")),
                len(config_lines)  # Default to appending at the end
            )

            # Ensure a single blank line before the new Match block
            if insert_index > 0 and config_lines[insert_index - 1].strip():
                config_lines.insert(insert_index, "\n")
                insert_index += 1

            # Insert the Match block
            config_lines[insert_index:insert_index] = match_block + ["\n"]

            # Write the updated configuration back to the file
            with sshd_config_path.open("w") as f:
                f.writelines(config_lines)

            print(f"Added Match User directive for {self.config.username} in sshd_config with proper spacing.")

        except Exception as e:
            print(f"Failed to update sshd_config for {self.config.username}: {e}")



    