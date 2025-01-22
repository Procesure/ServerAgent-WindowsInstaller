import subprocess
from pathlib import Path
from pydantic import StrictStr
from typing import Union, Tuple, Any, List


class BaseManager:


    program_data_path: Path = Path("C:\ProgramData\Procesure")
    program_files_path: Path = Path("C:\Program Files\Procesure")

    def __init__(self):

        self.program_data_path.mkdir(exist_ok=True)
        self.program_files_path.mkdir(exist_ok=True)
        self._powershell: Path = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")

    @property
    def powershell(self) -> Path:
        return self._powershell

    @property
    def server_agent_config_path(self) -> Path:
        return self.program_data_path / "server-agent.yml"

    @property
    def procesure_exe_path(self) -> Path:
        return self.program_files_path / "procesure.exe"

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

            print(msg_in)

            command = [f"{self.powershell} ", *cmd]

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