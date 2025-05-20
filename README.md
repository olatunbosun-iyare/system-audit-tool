# 🖥️ System Inventory & Audit Tool

A cross-platform Python script that collects system information, user sessions, disk usage, and installed software. It stores **all reports in a single JSON file** and keeps run metadata separately.

---

## 🚀 Features

- ✅ System info (hostname, OS, architecture, processor, RAM)
- 👥 Logged-in users (with human-readable login times)
- 💽 Disk usage per partition
- 📦 Installed software (Windows, Linux, macOS)
- 📄 Stores all reports in `system_reports.json`
- 📝 Run metadata (count, last run) stored in `run_log.json`
- 🔁 Supports scheduling with cron (Linux/macOS) or Task Scheduler (Windows)

---

## 🛠 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/system-inventory-audit.git
cd system-inventory-audit
```
