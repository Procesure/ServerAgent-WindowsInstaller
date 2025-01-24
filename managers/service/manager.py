import shutil
import time
import win32serviceutil
import win32service
import win32event
from pathlib import Path
from managers.manager import BaseManager
from typing import Union
import servicemanager
import sys


class ServiceManager(win32serviceutil.ServiceFramework):

    _svc_name_ = "procesure"
    _svc_display_name_ = "Procesure Service Manager"
    _svc_description_ = "Manages processes required by Procesure."

    def __init__(self, args):

        super().__init__(args)

        self.running = True
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server_process: Union[bool, None] = None
        self.agent_process: Union[bool, None] = None

    def SvcDoRun(self):

        """Main service logic."""

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main_loop()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def main_loop(self):
        while self.running:
            try:
                self.main()
                time.sleep(60)
            except Exception as e:
                print(e)
                self.running = False

    def SvcStop(self):

        """Cleanup logic when the service stops."""

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    @staticmethod
    def to_exe():

        svc_manager_path = Path("./managers/service/manager.py")
        svc_manager_full_path = Path(svc_manager_path.parent.resolve() / "manager.py")

        temp_output_dir = Path(r"C:\Temp")
        temp_output_dir.mkdir(parents=True, exist_ok=True)

        target_dir = Path(r"C:\Program Files\Procesure")
        target_dir.mkdir(parents=True, exist_ok=True)

        exe_name = "service-manager"

        cmd = [
            "pyinstaller",
            "--hidden-import=win32timezone",
            "--onefile",
            "--noconsole",
            f"--name={exe_name}",
            f"--distpath={temp_output_dir}",
            str(svc_manager_full_path)
        ]

        BaseManager.execute_command(
            cmd=cmd,
            msg_in="Creating Procesure Service Manager...",
            msg_out=f"Procesure Service Manager created successfully in {temp_output_dir}",
            msg_error="Failed to create Procesure Service Manager."
        )

        temp_exe_path = temp_output_dir / f"{exe_name}.exe"
        target_exe_path = target_dir / f"{exe_name}.exe"

        if temp_exe_path.exists():

            try:
                shutil.move(temp_exe_path, target_exe_path)
                print(f"Moved {temp_exe_path} to {target_exe_path}.")
            except Exception as e:
                print(f"Failed to move the executable: {e}")
        else:
            print(f"Executable not found in {temp_output_dir}.")

    @staticmethod
    def install_service():
        win32serviceutil.InstallService(
            exeName=r"C:\Program Files\Procesure\service-manager.exe",
            pythonClassString=ServiceManager._svc_name_,
            serviceName=ServiceManager._svc_name_,
            displayName=ServiceManager._svc_display_name_,
            description=ServiceManager._svc_description_,
            startType=win32service.SERVICE_AUTO_START
        )
        print("Service installed successfully.")

    @staticmethod
    def uninstall_service():

        """Uninstall the service from the system."""

        try:
            ServiceManager.stop_service()
            print("Service stopped successfully.")
        except Exception as e:
            print(f"Failed to stop the service: {e}")

        try:
            win32serviceutil.RemoveService(ServiceManager._svc_name_)
            print("Service uninstalled successfully.")
        except Exception as e:
            print(f"Failed to uninstall the service: {e}")

    @staticmethod
    def start_service():
        win32serviceutil.StartService(ServiceManager._svc_name_)
        print("Service started successfully.")

    @staticmethod
    def stop_service():
        win32serviceutil.StopService(ServiceManager._svc_name_)
        print("Service stopped successfully.")

    def __start_server(self):

        cmd = [f".//sshd -f '{self.server_config_path}'"]

        BaseManager.execute_bkg_command(
            cmd=cmd,
            msg_in="Starting Procesure Server...",
            msg_out=f"Procesure Server started successfully",
            msg_error="Failed to start Procesure Server.",
            cwd=self.server_program_files_path
        )

        self.server_process = True

    def __start_agent(self):

        cmd = [
            f".//agent start --all --config='{self.agent_config_path}'"
        ]

        BaseManager.execute_bkg_command(
            cmd=cmd,
            msg_in="Starting Procesure Agent...",
            msg_out=f"Procesure Agent started successfully.",
            msg_error="Failed to start Procesure Agent.",
            cwd=self.program_files_path
        )

        self.agent_process = True

    def main(self):

        if not self.server_process:
            self.__start_server()

        if not self.agent_process:
            self.__start_agent()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ServiceManager)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ServiceManager)