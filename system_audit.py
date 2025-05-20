import platform
import socket
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
        "RAM (GB)": get_total_memory()
    }


def get_total_memory():
    os_type = platform.system()

    try:
        if os_type == "Windows":
            output = subprocess.check_output(
                "wmic memorychip get capacity", shell=True)
            lines = output.decode().split()
            capacities = [int(x) for x in lines if x.isdigit()]
            return round(sum(capacities) / (1024 ** 3), 2)

        elif os_type == "Linux":
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            for line in meminfo.splitlines():
                if "MemTotal" in line:
                    kb = int(line.split()[1])
                    return round(kb / (1024 ** 2), 2)

        elif os_type == "Darwin":  # macOS
            output = subprocess.check_output(["sysctl", "hw.memsize"])
            mem_bytes = int(output.decode().split(":")[1].strip())
            return round(mem_bytes / (1024 ** 3), 2)

    except Exception as e:
        return f"Error: {e}"


def get_disk_usage():
    os_type = platform.system()
    disks = []

    try:
        if os_type == "Windows":
            output = subprocess.check_output(
                "wmic logicaldisk get deviceid,freespace,size", shell=True)
            lines = output.decode().splitlines()[1:]
            for line in lines:
                parts = line.split()
                if len(parts) == 3:
                    device, free, size = parts
                    if size.isdigit() and int(size) > 0:
                        used_percent = 100 - (int(free) / int(size)) * 100
                        disks.append({
                            "Device": device,
                            "Mount Point": device,
                            "Usage (%)": round(used_percent, 2)
                        })

        elif os_type in ["Linux", "Darwin"]:
            output = subprocess.check_output(["df", "-h", "/"])
            lines = output.decode().splitlines()[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 6:
                    device, size, used, avail, percent, mount = parts[:6]
                    disks.append({
                        "Device": device,
                        "Mount Point": mount,
                        "Usage (%)": percent
                    })

    except Exception as e:
        disks.append({"Error": str(e)})

    return disks


def get_logged_in_users():
    users = []
    try:
        output = subprocess.check_output("who", shell=True)
        lines = output.decode().splitlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                username = parts[0]
                login_time = " ".join(parts[2:4]) if len(
                    parts) >= 4 else parts[2]
                users.append({
                    "Username": username,
                    "Login Time": login_time
                })
    except Exception as e:
        users.append({"Error": str(e)})

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

        elif os_type == "Darwin":
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
    run_log = load_run_log()
    run_count = run_log.get("run_count", 0) + 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
