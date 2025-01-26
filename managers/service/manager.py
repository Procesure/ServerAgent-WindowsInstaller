import shutil
import win32serviceutil
import win32service
from pathlib import Path
from managers.manager import BaseManager, GUILogger
from service.service import Service


class ServiceManager(BaseManager):

    def __init__(self, logger: GUILogger):
        super().__init__(logger)

    def to_exe(self):

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

    def install_service(self):

        win32serviceutil.InstallService(
            exeName=r"C:\Program Files\Procesure\service-manager.exe",
            pythonClassString=Service.name,
            serviceName=Service.name,
            displayName=Service.display_name,
            description=Service.description,
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
            win32serviceutil.RemoveService(ServiceManager.svc_name)
            self.logger.log("Service uninstalled successfully.")
        except Exception as e:
            self.logger.log(f"Failed to uninstall the service: {e}")

    def start_service(self):
        win32serviceutil.StartService(ServiceManager.svc_name)
        self.logger.log("Service started successfully.")

    def stop_service(self):
        win32serviceutil.StopService(ServiceManager.svc_name)
        self.logger.log("Service stopped successfully.")