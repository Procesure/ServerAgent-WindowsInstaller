import subprocess
from pathlib import Path
from typing import Union, List, Tuple, Any
from pydantic import StrictStr
from service.logger import svc_logger


class CommandExecutor:

    powershell: Path = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")

    def __init__(self):
        self.logger = svc_logger

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

            command = [f"{self.powershell} ", *cmd]

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

            command = [f"{self.powershell} ", *cmd]

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