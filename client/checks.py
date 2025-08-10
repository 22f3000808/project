import platform
import subprocess
import json

def check_disk_encryption():
    sys = platform.system()
    if sys == "Darwin":
        out = subprocess.run(["fdesetup", "status"], capture_output=True, text=True)
        return {"value": "On" in out.stdout, "details": out.stdout.strip()}
    elif sys == "Linux":
        out = subprocess.run(["lsblk", "-o", "NAME,FSTYPE"], capture_output=True, text=True)
        return {"value": "crypto_LUKS" in out.stdout, "details": out.stdout.strip()}
    elif sys == "Windows":
        cmd = [
            "powershell",
            "-Command",
            "Get-BitLockerVolume | Select MountPoint,ProtectionStatus | ConvertTo-Json"
        ]
        out = subprocess.run(cmd, capture_output=True, text=True)
        try:
            data = json.loads(out.stdout)
        except:
            data = out.stdout
        return {"value": "On" in str(out.stdout), "details": data}
    else:
        return {"value": None, "details": "Unsupported OS"}

def check_os_updates():
    sys = platform.system()
    if sys == "Darwin":
        out = subprocess.run(["softwareupdate", "-l"], capture_output=True, text=True)
        return {"value": "No new software available" in out.stdout, "details": out.stdout}
    elif sys == "Linux":
        out = subprocess.run(["bash", "-lc", "apt-get -s upgrade"], capture_output=True, text=True)
        return {"value": "0 upgraded" in out.stdout, "details": out.stdout}
    elif sys == "Windows":
        return {"value": None, "details": {"version": platform.version()}}
    else:
        return {"value": None, "details": "Unsupported OS"}

def check_antivirus():
    sys = platform.system()
    if sys == "Windows":
        cmd = [
            "powershell",
            "-Command",
            "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | ConvertTo-Json"
        ]
        out = subprocess.run(cmd, capture_output=True, text=True)
        try:
            data = json.loads(out.stdout)
        except:
            data = out.stdout
        return {"present": bool(data), "details": data}
    else:
        return {"present": False, "details": "Not implemented for this OS"}

def check_sleep_setting():
    sys = platform.system()
    if sys == "Darwin":
        out = subprocess.run(["pmset", "-g"], capture_output=True, text=True)
        return {"value": None, "details": out.stdout}
    elif sys == "Windows":
        out = subprocess.run(["powercfg", "/query"], capture_output=True, text=True)
        return {"value": None, "details": out.stdout}
    else:
        return {"value": None, "details": "Not implemented"}
