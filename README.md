# Remote Access Agent Installer

## Overview

This Python script automates the setup of remote access capabilities on a Windows machine, providing a convenient way to establish remote connectivity using SSH and Remote Desktop.

## Installation

### Download Executable

1. Go to the [Latest Release](https://github.com/Procesure/ProcesureWindowsAgent/releases/latest) page
2. Download the latest `agent.exe`

### Running the Agent

**IMPORTANT: The agent MUST be run with Administrator Privileges**

Methods to run with admin rights:
- Right-click `agent.exe` and select "Run as administrator"
- Open Command Prompt as an Administrator, navigate to the download directory, and run `agent.exe`

## System Requirements

- Windows Operating System
- Administrator Account
- Internet Connection
- Minimal system resources

## Features

- Automatic Procesure agent installation
- SSH service enablement
- Remote Desktop activation
- Procesure agent service configuration

## Configuration

Before running, ensure you put the `agent.yml` configuration file provided in `C:\procesure\agent.yml`.


## Troubleshooting

- Ensure you're running with administrator rights
- Verify internet connectivity

## Support

If you encounter any issues, please open a GitHub issue with detailed information about your system and the specific problem you're experiencing.

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Distributed under the MIT License. See LICENSE.txt for more information.