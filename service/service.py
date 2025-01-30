import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import psutil

from service.cmd_executor import CommandExecutor, svc_logger
from managers.manager import BaseManager


class Service(win32serviceutil.ServiceFramework):

    _svc_name_ = "procesure"
    
    svc_name = "procesure"
    svc_display_name = "Procesure Service Manager"
    svc_description = "Manages processes required by Procesure."

    def __init__(self, args):

        self.logger = svc_logger
        self.logger.log(message="Initiating procesure service")

        self.cmd = CommandExecutor()
        self.logger.log(message="Command executor initiated")

        try:

            super().__init__(args)

            self.running = True
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.server_process_running: bool = False
            self.agent_process_running: bool = False

            self.logger.log(message="Finished instantiating service")

        except BaseException as e:
            self.logger.log(message=str(e), level="error")


    def SvcDoRun(self):

        """Main service logic."""

        self.logger.log(message="Running service")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main_loop()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
    def SvcStop(self):

        """Cleanup logic when the service stops."""

        self.logger.log(message="Stop service signal received.")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

        self.__stop_process_by_path(BaseManager.server_exe_path.__str__())
        self.__stop_process_by_path(BaseManager.agent_exe_path.__str__())

        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def __stop_process_by_path(self, executable_path: str):

        """
        Stops processes that match the specified executable path.

        :param executable_path: Full path to the executable to look for, case-insensitively.
        """

        executable_path = executable_path.lower()

        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['exe'] and proc.info['exe'].lower() == executable_path:
                    self.logger.log(f"Stopping {proc.info['name']} with PID {proc.info['pid']}")
                    proc.terminate()
                    proc.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except psutil.TimeoutExpired:
                print(f"Process {proc.info['pid']} did not terminate in time and will be killed.")
                proc.kill()

        self.logger.log("Process stop attempt completed.")

    def __stop_server(self):

        """Method to stop the SSH server."""

        if self.server_process_running:
            try:
                stop_cmd = [".//sshd -f '{0}' -O stop".format(BaseManager.server_config_path)]
                self.cmd.execute_bkg_command(
                    cmd=stop_cmd,
                    msg_in="Stopping Procesure SSH Server",
                    msg_out="Procesure SSH Server stopped successfully.",
                    msg_error="Failed to stop Procesure SSH Server",
                    cwd=BaseManager.server_program_files_path
                )
                self.server_process_running = False
            except BaseException as e:
                self.logger.log(str(e), level="error")

    def __stop_agent(self):

        """Method to stop the Ngrok agent."""

        if self.agent_process_running:
            try:
                stop_cmd = [".//agent stop --all --config='{0}'".format(BaseManager.agent_config_path)]
                self.cmd.execute_bkg_command(
                    cmd=stop_cmd,
                    msg_in="Stopping Procesure Agent...",
                    msg_out="Procesure Agent stopped successfully.",
                    msg_error="Failed to stop Procesure Agent.",
                    cwd=BaseManager.program_files_path
                )
                self.agent_process_running = False
            except BaseException as e:
                self.logger.log(str(e), level="error")
        
    def __start_server(self):

        try:

            cmd = [f".//sshd -f '{BaseManager.server_config_path}'"]

            self.cmd.execute_bkg_command(
                cmd=cmd,
                msg_in="Starting Procesure SSH Server",
                msg_error="Failed to Start Procesure SSH Server",
                msg_out="Procesure SSH Server started with success",
                cwd=BaseManager.server_program_files_path
            )

            self.server_process_running = True

        except BaseException as e:
            self.logger.log(str(e))

    def __start_agent(self):

        try:

            cmd = [f".//agent start --all --config='{BaseManager.agent_config_path}'"]

            self.cmd.execute_bkg_command(
                cmd=cmd,
                msg_in="Starting Procesure Agent...",
                msg_out=f"Procesure Agent started successfully.",
                msg_error="Failed to start Procesure Agent.",
                cwd=BaseManager.program_files_path
            )

            self.agent_process_running = True

        except BaseException as e:
            self.logger.log(str(e))

    def main_loop(self):

        self.logger.log("Entering service main loop")

        while self.running:
            try:
                self.main()
                time.sleep(60)
            except Exception as e:
                print(e)
                self.running = False

    def main(self):

        self.logger.log(message="Entering service logic method")

        if not self.server_process_running:
            self.__start_server()

        if not self.agent_process_running:
            self.__start_agent()

if __name__ == '__main__':

    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(Service)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(Service)