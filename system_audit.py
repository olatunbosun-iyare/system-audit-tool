import platform
import socket
import json
import subprocess
import os
import psutil
from datetime import datetime
from getmac import get_mac_address


def get_system_info():
    # Get IP address by connecting to a public DNS (doesn't actually send data)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        ip_address = "127.0.0.1"

    return {
        "Hostname": socket.gethostname(),
        "Operating System": f"{platform.system()} {platform.release()}",
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "IP Address": ip_address,
        "MAC Address": get_mac_address(),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2)
    }


def get_disk_usage():
    disks = []
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            # Skip pseudo filesystems
            if 'cdrom' in partition.opts or partition.fstype == '':
                continue
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "Device": partition.device,
                    "Mount Point": partition.mountpoint,
                    "File System Type": partition.fstype,
                    "Total Size (GB)": round(usage.total / (1024 ** 3), 2),
                    "Used (GB)": round(usage.used / (1024 ** 3), 2),
                    "Free (GB)": round(usage.free / (1024 ** 3), 2),
                    "Usage (%)": usage.percent
                })
            except PermissionError:
                # Disk might not be accessible
                continue
    except Exception as e:
        disks.append({"Error": str(e)})

    return disks


def get_logged_in_users():
    users_list = []
    try:
        users = psutil.users()
        for user in users:
            login_time = datetime.fromtimestamp(user.started).strftime("%Y-%m-%d %H:%M:%S")
            users_list.append({
                "Username": user.name,
                "Terminal": user.terminal,
                "Login Time": login_time
            })
    except Exception as e:
        users_list.append({"Error": str(e)})

    return users_list


def get_installed_software():
    software_list = []
    os_type = platform.system()

    try:
        if os_type == "Windows":
            # Keeping wmic for Windows as it's standard, though slow
            output = subprocess.check_output(
                ['wmic', 'product', 'get', 'name'], shell=True)
            lines = output.decode(errors="ignore").split('\n')
            for line in lines[1:]:
                name = line.strip()
                if name:
                    software_list.append(name)

        elif os_type == "Linux":
            if os.path.exists("/usr/bin/dpkg"):
                output = subprocess.check_output(['dpkg', '--get-selections'])
                lines = output.decode(errors="ignore").split('\n')
                for line in lines:
                    if line:
                        software_list.append(line.split()[0]) # Just the package name
            else:
                output = subprocess.check_output(['rpm', '-qa'])
                lines = output.decode(errors="ignore").split('\n')
                for line in lines:
                    if line:
                        software_list.append(line.strip())

        elif os_type == "Darwin":
            # Using mdfind for faster lookup of apps in /Applications
            # system_profiler is too slow and verbose
            try:
                output = subprocess.check_output(['mdfind', 'kMDItemContentType == "com.apple.application-bundle" -onlyin /Applications'])
                lines = output.decode(errors="ignore").split('\n')
                for line in lines:
                    if line.strip():
                        # Get just the app name from the path
                        app_name = os.path.basename(line.strip())
                        software_list.append(app_name)
            except Exception:
                # Fallback if mdfind fails
                software_list.append("Error fetching software list")

    except Exception as e:
        software_list.append(f"Error fetching software list: {str(e)}")

    return sorted(software_list)


REPORTS_FILE = "system_reports.json"
RUN_LOG_FILE = "run_log.json"


def load_reports():
    if os.path.exists(REPORTS_FILE):
        try:
            with open(REPORTS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    else:
        return []


def save_reports(reports):
    with open(REPORTS_FILE, "w") as f:
        json.dump(reports, f, indent=4)


def load_run_log():
    if os.path.exists(RUN_LOG_FILE):
        try:
            with open(RUN_LOG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
             return {"run_count": 0, "last_run": None}
    else:
        return {"run_count": 0, "last_run": None}


def save_run_log(run_log):
    with open(RUN_LOG_FILE, "w") as f:
        json.dump(run_log, f, indent=4)


if __name__ == "__main__":
    run_log = load_run_log()
    run_count = run_log.get("run_count", 0) + 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"🔄 Generating system audit report #{run_count}...")

    new_report = {
        "Report Number": run_count,
        "Generated At": now,
        "System Information": get_system_info(),
        "Disk Usage": get_disk_usage(),
        "Logged-in Users": get_logged_in_users(),
        "Installed Software": get_installed_software()
    }

    reports = load_reports()
    reports.append(new_report)
    save_reports(reports)

    run_log["run_count"] = run_count
    run_log["last_run"] = now
    save_run_log(run_log)

    print(f"✅ Report #{run_count} saved at {now} in '{REPORTS_FILE}'")
    print(f"ℹ️ Run log updated in '{RUN_LOG_FILE}'")
