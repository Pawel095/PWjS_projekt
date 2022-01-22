import ctypes
import platform
import subprocess
import sys

import psutil


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def UAC_elevate() -> None:
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        " ".join(sys.argv),
        None,
        1,
    )


def get_temp():
    system = platform.system()
    if system == "Linux":
        return [str(a.current) for a in psutil.sensors_temperatures()["cpu_thermal"]]
    elif system == "Windows":
        if is_admin():
            return (
                subprocess.run(
                    'C:\Windows\System32\WindowsPowerShell\\v1.0\powershell.exe Get-CimInstance MSAcpi_ThermalZoneTemperature -Namespace "root/wmi" | Select-Object CurrentTemperature | ForEach-Object {$_.CurrentTemperature/10 - 273.15}',
                    capture_output=True,
                )
                .stdout.decode("utf-8")
                .split("\r\n")[:-1]
            )
        else:
            return ["0"]
    else:
        return ["0"]
