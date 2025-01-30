import shutil
from managers.manager import BaseManager
from gui.logger import gui_logger

from pathlib import Path


class TaskManager(BaseManager):

    def __init__(self):
        super().__init__(gui_logger)

    def copy_run_task_script(self):

        source_path = "./scripts/RunTask.ps1"
        destination_path = Path(self.program_files_path / "RunTask.ps1")

        self.logger.log(f"Copying StartRDP.ps1 file {destination_path}")

        shutil.copy(source_path, destination_path)
        self.logger.log(f"Start RDP file copied to {destination_path}")

    def copy_start_rdp_file(self):

        """Copies an RDP configuration file to the specified directory."""

        source_path = "./scripts/StartRDP.ps1"
        destination_path = Path(self.program_files_path / "StartRDP.ps1")

        self.logger.log(f"Copying StartRDP.ps1 file {destination_path}")

        shutil.copy(source_path, destination_path)
        self.logger.log(f"Start RDP file copied to {destination_path}")

    def handle_installation(self):

        """High-level method to handle the entire setup process."""

        try:

            self.copy_run_task_script()
            self.copy_start_rdp_file()

        except Exception as e:

            self.logger.log(f"Installation failed: {e}", level="error")