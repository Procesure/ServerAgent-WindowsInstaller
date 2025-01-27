import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys

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

        self.logger.log(message="Accessing service entry point")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main_loop()
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        
    def SvcStop(self):

        """Cleanup logic when the service stops."""

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
        
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
        while self.running:
            try:
                self.main()
                time.sleep(60)
            except Exception as e:
                print(e)
                self.running = False

    def main(self):

        self.logger.log(message="Entering main method")

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