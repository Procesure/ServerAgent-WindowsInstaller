import shutil
import requests
import win32serviceutil
import win32service
from pathlib import Path
from managers.manager import BaseManager
from service.service import Service

from gui.logger import gui_logger
from pydantic import StrictStr


class ServiceManager(BaseManager):

    cpp_redist_exe_download_url: StrictStr = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    vc_redist_path: Path = Path(BaseManager.program_files_path / "vc_redist.exe")

    def __init__(self):
        super().__init__(gui_logger)

    def to_exe(self):

        self.download_vc_redist()
        self.install_vc_redist()

        svc_manager_path = Path("./service/service.py")
        svc_manager_full_path = Path(svc_manager_path.parent.resolve() / "service.py")

        temp_output_dir = Path(r"C:\Temp")
        temp_output_dir.mkdir(parents=True, exist_ok=True)

        exe_name = "service"

        cmd = [
            "pyinstaller",
            "--hidden-import=win32timezone",
            "--onefile",
            "--noconsole",
            f"--name={exe_name}",
            f"--distpath={temp_output_dir}",
            str(svc_manager_full_path)
        ]

        self.execute_command(
            cmd=cmd,
            msg_in="Creating Procesure Service Manager...",
            msg_out=f"Procesure Service Manager created successfully in {temp_output_dir}",
            msg_error="Failed to create Procesure Service Manager."
        )

        temp_exe_path = temp_output_dir / f"{exe_name}.exe"
        target_exe_path = self.program_files_path / f"{exe_name}.exe"

        if temp_exe_path.exists():

            try:
                shutil.move(temp_exe_path, target_exe_path)
                print(f"Moved {temp_exe_path} to {target_exe_path}.")
            except Exception as e:
                print(f"Failed to move the executable: {e}")
        else:
            print(f"Executable not found in {temp_output_dir}.")

    def download_vc_redist(self):

        """
        Downloads the Visual C++ Redistributable package and saves it to the Procesure directory.
        """

        try:

            if self.vc_redist_path.exists():
                self.logger.log(f"Visual C++ Redistributable already downloaded, skipping download...")
                return

            self.logger.log(f"Downloading Visual C++ Redistributable from {self.cpp_redist_exe_download_url}...")
            response = requests.get(self.cpp_redist_exe_download_url, stream=True)
            response.raise_for_status()
            with open(self.vc_redist_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.logger.log(f"Downloaded Visual C++ Redistributable to {self.vc_redist_path}")
            return self.vc_redist_path
        except Exception as e:
            self.logger.log(f"Failed to download Visual C++ Redistributable: {e}")
            return None

    def install_vc_redist(self):

        """
        Installs the Visual C++ Redistributable package from the specified path.
        """

        try:

            if not self.vc_redist_path.exists():
                self.logger.log(f"Executable not found at {self.vc_redist_path}")
                return

            self.execute_command(
                cmd=[".//vc_redist", "/quiet", "/norestart"],
                msg_in="Installing Visual C++ Redistributable",
                msg_out="Visual C++ Redistributable installed successfully.",
                cwd=self.program_files_path
            )

        except Exception as e:
            self.logger.log(f"Failed to install Visual C++ Redistributable: {e}")

    def install_service(self):

        win32serviceutil.InstallService(
            exeName=self.service_exe_path.__str__(),
            pythonClassString=Service.svc_name,
            serviceName=Service.svc_name,
            displayName=Service.svc_display_name,
            description=Service.svc_description,
            startType=win32service.SERVICE_AUTO_START
        )

        self.logger.log("Service installed successfully.")

    def uninstall_service(self):

        """Uninstall the service from the system."""

        try:
            self.stop_service()
            self.logger.log("Service stopped successfully.")
        except Exception as e:
            self.logger.log(f"Failed to stop the service: {e}")

        try:
            win32serviceutil.RemoveService(Service.svc_name)
            self.logger.log("Service uninstalled successfully.")
        except Exception as e:
            self.logger.log(f"Failed to uninstall the service: {e}")

    def start_service(self):

        win32serviceutil.StartService(Service.svc_name)
        self.logger.log("Service started successfully.")

    def stop_service(self):
        win32serviceutil.StopService(Service.svc_name)
        self.logger.log("Service stopped successfully.")