import subprocess
from pathlib import Path
from pydantic import StrictStr
from typing import Union, Tuple, Any, List
from gui.logger import GUILogger
from service.logger import ServiceLogger


class BaseManager:

    program_data_path: Path = Path("C:\ProgramData\Procesure")
    program_files_path: Path = Path("C:\Program Files\Procesure")

    server_program_files_path: Path = program_files_path / "server"
    server_program_data_path: Path = program_data_path / "ssh"

    server_exe_path: Path = server_program_files_path / "sshd.exe"
    server_config_path: Path = server_program_data_path / "sshd_config"

    agent_exe_path: Path = program_files_path / "agent.exe"
    agent_config_path: Path = program_data_path / "agent-config.yml"

    service_exe_path: Path = Path(r"C:\Program Files\Procesure\procesure-svc.exe")

    powershell: Path = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")

    def __init__(self, logger: Union[ServiceLogger, GUILogger]):

        self.logger = logger
        self.make_program_dirs()

    @staticmethod
    def make_program_dirs():

        BaseManager.program_data_path.mkdir(exist_ok=True)
        BaseManager.program_files_path.mkdir(exist_ok=True)

    def execute_command(
        self,
        cmd: List[StrictStr],
        msg_in: StrictStr = None,
        msg_out: StrictStr = None,
        msg_error: StrictStr = None,
        *args,
        **kwargs
    ) -> Union[
        Tuple[int, subprocess.CompletedProcess[str]],
        Tuple[int, subprocess.CalledProcessError],
        Tuple[int, Any]
    ]:

        try:

            self.logger.log(message=msg_in)

            command = [f"{BaseManager.powershell} ", *cmd]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                *args,
                **kwargs
            )

            self.logger.log(message=f"Command: {result.args}")
            self.logger.log(message=f"Exit Code: {result.returncode}")
            self.logger.log(message=f"Output: {result.stdout}")

            if result.stderr:
                self.logger.log(f"Error: {result.stderr}")

            self.logger.log(msg_out)

            return 0, result

        except subprocess.CalledProcessError as e:
            self.logger.log(msg_error)
            self.logger.log("Error details:")
            self.logger.log(f"Command: {e.cmd}")
            self.logger.log(f"Return code: {e.returncode}")
            self.logger.log(f"Output: {e.output}")
            self.logger.log(f"Error: {e.stderr}")
            return 1, e

        except Exception as e:
            print(msg_error)
            print(f"Unexpected error occurred: {e}")
            return 2, e

    def execute_bkg_command(
        self,
        cmd: List[StrictStr],
        msg_in: StrictStr = None,
        msg_out: StrictStr = None,
        msg_error: StrictStr = None,
        *args,
        **kwargs
    ) -> Union[
        Tuple[int, subprocess.Popen],
        Tuple[int, Exception]
    ]:

        try:

            if msg_in:
                self.logger.log(msg_in)

            command = [f"{BaseManager.powershell} ", *cmd]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                *args,
                **kwargs
            )

            self.logger.log(f"Command initiated: {' '.join(command)}")

            if msg_out:
                self.logger.log(msg_out)

            return 0, process

        except Exception as e:
            if msg_error:
                self.logger.log(msg_error)
            self.logger.log(f"Failed to start process: {e}")
            return 1, e


