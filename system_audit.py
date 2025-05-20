import platform
import socket
import psutil
from getmac import get_mac_address
import json
import subprocess
import os
from datetime import datetime


def get_system_info():
    return {
        "Hostname": socket.gethostname(),
        "Operating System": f"{platform.system()} {platform.release()}",
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "IP Address": socket.gethostbyname(socket.gethostname()),
        "MAC Address": get_mac_address(),
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2)
    }


def get_disk_usage():
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "Device": partition.device,
                "Mount Point": partition.mountpoint,
                "Usage (%)": usage.percent
            })
        except PermissionError:
            continue
    return disks


def get_logged_in_users():
    users = []
    for user in psutil.users():
        readable_time = datetime.fromtimestamp(
            user.started).strftime("%Y-%m-%d %H:%M:%S")
        users.append({
            "Username": user.name,
            "Login Time": readable_time
        })
    return users


def get_installed_software():
    software_list = []
    os_type = platform.system()

    try:
        if os_type == "Windows":
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
            else:
                output = subprocess.check_output(['rpm', '-qa'])
            lines = output.decode(errors="ignore").split('\n')
            for line in lines:
                if line:
                    software_list.append(line.strip())

        elif os_type == "Darwin":  # macOS
            output = subprocess.check_output(
                ['system_profiler', 'SPApplicationsDataType'])
            lines = output.decode(errors="ignore").split('\n')
            for line in lines:
                if "Location:" in line:
                    software_list.append(line.strip())

    except Exception as e:
        software_list.append(f"Error fetching software list: {str(e)}")

    return software_list


REPORTS_FILE = "system_reports.json"
RUN_LOG_FILE = "run_log.json"


def load_reports():
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, "r") as f:
            return json.load(f)
    else:
        return []


def save_reports(reports):
    with open(REPORTS_FILE, "w") as f:
        json.dump(reports, f, indent=4)


def load_run_log():
    if os.path.exists(RUN_LOG_FILE):
        with open(RUN_LOG_FILE, "r") as f:
            return json.load(f)
    else:
        return {"run_count": 0, "last_run": None}


def save_run_log(run_log):
    with open(RUN_LOG_FILE, "w") as f:
        json.dump(run_log, f, indent=4)


if __name__ == "__main__":
    # Load run log to get previous count
    run_log = load_run_log()
    run_count = run_log.get("run_count", 0) + 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the new report data (replace these with your actual functions)
    new_report = {
        "Report Number": run_count,
        "Generated At": now,
        "System Information": get_system_info(),
        "Disk Usage": get_disk_usage(),
        "Logged-in Users": get_logged_in_users(),
        "Installed Software": get_installed_software()
    }

    # Load existing reports, append new one, then save
    reports = load_reports()
    reports.append(new_report)
    save_reports(reports)

    # Update and save run log
    run_log["run_count"] = run_count
    run_log["last_run"] = now
    save_run_log(run_log)

    print(f"✅ Report #{run_count} saved at {now} in '{REPORTS_FILE}'")
    print(f"ℹ️ Run log updated in '{RUN_LOG_FILE}'")
