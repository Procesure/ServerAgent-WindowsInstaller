import subprocess
from pathlib import Path
from pydantic import StrictStr
from typing import Union, Tuple, Any, List


class BaseManager:


    program_data_path: Path = Path("C:\ProgramData\Procesure")
    program_files_path: Path = Path("C:\Program Files\Procesure")
    powershell: Path = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")

    def __init__(self):

        self.program_data_path.mkdir(exist_ok=True)
        self.program_files_path.mkdir(exist_ok=True)

    @property
    def server_agent_config_path(self) -> Path:
        return self.program_data_path / "agent.yml"

    @property
    def procesure_exe_path(self) -> Path:
        return self.program_files_path / "agent.exe"

    @staticmethod
    def execute_command(
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

            print(msg_in)

            command = [f"{BaseManager.powershell} ", *cmd]

            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                *args,
                **kwargs
            )

            print("Command:", result.args)
            print("Exit Code:", result.returncode)
            print("Output:", result.stdout)

            if result.stderr:
                print("Error:", result.stderr)

            print(msg_out)

            return 0, result

        except subprocess.CalledProcessError as e:
            print(msg_error)
            print("Error details:")
            print(f"Command: {e.cmd}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")
            print(f"Error: {e.stderr}")
            return 1, e

        except Exception as e:
            print(msg_error)
            print(f"Unexpected error occurred: {e}")
            return 2, e

    @staticmethod
    def execute_bkg_command(
        cmd: List[StrictStr],
        msg_in: StrictStr = None,
        msg_out: StrictStr = None,
        msg_error: StrictStr = None,
        log: callable = None,
        *args,
        **kwargs
    ) -> Union[
        Tuple[int, subprocess.Popen],
        Tuple[int, Exception]
    ]:

        try:

            if msg_in:
                if log:
                    log(msg_in)
                else:
                    print(msg_in)

            command = [f"{BaseManager.powershell} ", *cmd]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                *args,
                **kwargs
            )

            print(f"Command initiated: {' '.join(command)}")

            if msg_out:
                print(msg_out)

            return 0, process

        except Exception as e:
            if msg_error:
                if log:
                    log(msg_error)
                else:
                    print(msg_error)
                print(msg_error)
            if log:
                log(str(e))
            else:
                print(e)
            print(f"Failed to start process: {e}")
            return 1, e