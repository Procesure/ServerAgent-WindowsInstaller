import shutil
import win32serviceutil
import win32service
import win32event
from pathlib import Path
from managers.manager import BaseManager


class ServiceManager(win32serviceutil.ServiceFramework):

    _svc_name_ = "procesure"
    _svc_display_name_ = "Procesure Service Manager"
    _svc_description_ = "Manages processes required by Procesure."

    def __init__(self, args):

        super().__init__(args)

        self.sshd_exe = Path(r"C:\Program Files\Procesure\OpenSSH-Win64\sshd.exe")
        self.sshd_config = Path(r"C:\ProgramData\Procesure\ssh\sshd_config")
        self.server_agent_exe = Path(r"C:\Program Files\Procesure\server-agent.exe")
        self.server_agent_config = Path(r"C:\ProgramData\Procesure\server-agent.yml")

        self.running = False
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.sshd_process = None
        self.ngrok_process = None

    def start_open_ssh(self):
        pass

    def start_ngrok(self):
        pass

    def SvcDoRun(self):

        """Main service logic."""

        self.main()

    def SvcStop(self):

        """Cleanup logic when the service stops."""

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    @staticmethod
    def to_exe():

        svc_manager_path = Path('managers/service/manager.py')

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
            str(svc_manager_path)
        ]

        base_manager = BaseManager()

        base_manager.execute_command(
            cmd,
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

    def main(self):

        self.start_open_ssh()
        self.start_ngrok()