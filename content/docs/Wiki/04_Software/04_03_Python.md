---
title: Python Setup
layout: default
parent: 5. Software
nav_order: 3
---

# Python Setup

Python is useful for automation, data logging and communicating with a microcontroller over USB Serial.

## Install Python

Download a current stable Python 3 release from [python.org](https://www.python.org/downloads/). Follow the installer for your operating system.

On Windows, select the option that makes Python available from the command line if the installer offers it. On a managed university computer, use the installed version or ask before installing software.

## Check the installation

Open Terminal, PowerShell or Command Prompt:

```text
python --version
```

If that command is not recognised on Windows, try:

```text
py --version
```

On some macOS and Linux systems, use:

```text
python3 --version
```

## Create a project environment

A virtual environment keeps one project's packages separate:

```text
python -m venv .venv
```

Activate it:

```text
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS or Linux
source .venv/bin/activate
```

Install only the packages the project requires:

```text
python -m pip install pyserial
```

## Test Serial communication

```python
import serial

with serial.Serial("COM4", 115200, timeout=1) as board:
    while True:
        line = board.readline().decode(errors="replace").strip()
        if line:
            print(line)
```

Replace `COM4` with your board's port. On macOS or Linux, ports usually look like `/dev/tty...`.

Close Arduino Serial Monitor before running the script because both programs cannot normally open the same port simultaneously.

{: .tip}
> Save dependencies with `python -m pip freeze > requirements.txt`, but review the file before committing it.
