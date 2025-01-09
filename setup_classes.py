import subprocess
import sys
import os


class Windows11Setup:
    def install_openssh(self, ssh_keys_path):
        try:
            # Check if OpenSSH is already installed
            check_command = [
                "powershell",
                "-Command",
                "Get-WindowsCapability -Online | Where-Object { $_.Name -like '*OpenSSH*' }",
            ]

            process = subprocess.run(
                check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if "Installed" in process.stdout:
                print("OpenSSH is already installed on Windows 11.")
                return

            # Install OpenSSH
            print("Installing OpenSSH on Windows 11...")
            install_commands = [
                "powershell",
                "-Command",
                "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0",
            ]
            subprocess.run(install_commands, check=True)

            # Configure and start service
            service_commands = [
                "powershell",
                "-Command",
                "Start-Service sshd; Set-Service -Name sshd -StartupType Automatic",
            ]
            subprocess.run(service_commands, check=True)

        except subprocess.CalledProcessError as e:
            print(f"Failed to install OpenSSH on Windows 11: {e}")
            raise

    @staticmethod
    def enable_rdp():
        try:
            print("Enabling RDP for Windows 11...")
            commands = [
                [
                    "powershell",
                    "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0",
                ],
                [
                    "powershell",
                    "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp' -Name 'UserAuthentication' -Value 1",
                ],
            ]

            for cmd in commands:
                subprocess.run(cmd, check=True)

            print("RDP enabled successfully on Windows 11")

        except subprocess.CalledProcessError as e:
            print(f"Error enabling RDP on Windows 11: {e}")
            raise


class Windows10Setup:
    def install_openssh(self, ssh_keys_path):
        try:
            # Check if OpenSSH is already installed
            check_command = [
                "powershell",
                "-Command",
                "Get-WindowsCapability -Online | Where-Object { $_.Name -like '*OpenSSH*' }",
            ]

            process = subprocess.run(
                check_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if "Installed" in process.stdout:
                print("OpenSSH is already installed on Windows 10.")
                return

            # Install OpenSSH
            print("Installing OpenSSH on Windows 10...")
            install_command = [
                "powershell",
                "-Command",
                "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0",
            ]
            subprocess.run(install_command, check=True)

            # Start and configure service
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Start-Service sshd; Set-Service -Name sshd -StartupType Automatic",
                ],
                check=True,
            )

        except subprocess.CalledProcessError as e:
            print(f"Failed to install OpenSSH on Windows 10: {e}")
            raise

    @staticmethod
    def enable_rdp():
        try:
            print("Enabling RDP for Windows 10...")
            commands = [
                [
                    "powershell",
                    "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0",
                ],
                [
                    "powershell",
                    "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp' -Name 'UserAuthentication' -Value 1",
                ],
            ]

            for cmd in commands:
                subprocess.run(cmd, check=True)

            print("RDP enabled successfully on Windows 10")

        except subprocess.CalledProcessError as e:
            print(f"Error enabling RDP on Windows 10: {e}")
            raise


class WindowsServer2016Setup:
    def install_openssh(self, ssh_keys_path):
        try:
            try:
                subprocess.run(["powershell", f"mkdir {self.openssh_path}"], check=True)
            except Exception as e:
                print(e)

            # Run both the TLS setup and the download in the same PowerShell command
            subprocess.run(
                [
                    "powershell",
                    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "  # Set TLS protocol
                    f"Invoke-WebRequest -Uri 'https://github.com/PowerShell/Win32-OpenSSH/releases/download/V8.6.0.0p1-Beta/OpenSSH-Win64.zip' -OutFile '{self.openssh_path}\\openssh.zip'",
                ],
                check=True,
            )

            # Extract the downloaded OpenSSH zip
            subprocess.run(
                [
                    "powershell",
                    f"Expand-Archive -Path '{self.openssh_path}\\openssh.zip' -DestinationPath '{self.openssh_path}\\openssh'",
                ],
                check=True,
            )

            # Add OpenSSH to the system PATH
            subprocess.run(
                [
                    "powershell",
                    f"setx PATH '$env:path;{self.openssh_path}\\openssh\\' -m",
                ],
                check=True,
            )

            # Install OpenSSH
            subprocess.run(
                [
                    "powershell",
                    f"powershell.exe -ExecutionPolicy Bypass -File '{self.openssh_path}\\openssh\\OpenSSH-Win64\\install-sshd.ps1'",
                ],
                check=True,
            )

            # Allow inbound SSH traffic through the firewall
            try:
                subprocess.run(
                    [
                        "powershell",
                        "New-NetFirewallRule -Name sshd -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22",
                    ],
                    check=True,
                )
            except Exception as e:
                print(e)

            # Start SSH service
            subprocess.run(["powershell", "net start sshd"], check=True)

            # Set SSH service to start automatically on system restart
            subprocess.run(
                ["powershell", "Set-Service sshd -StartupType Automatic"], check=True
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
                [
                    "powershell",
                    "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0",
                ],
                [
                    "powershell",
                    "-Command",
                    "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp' -Name 'UserAuthentication' -Value 1",
                ],
            ]

            for cmd in commands:
                subprocess.run(cmd, check=True)

            print("RDP enabled successfully on Windows Server 2016")

        except subprocess.CalledProcessError as e:
            print(f"Error enabling RDP on Windows Server 2016: {e}")
            raise
