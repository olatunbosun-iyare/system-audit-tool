# System Inventory & Audit Tool

## Product Overview
The **System Inventory & Audit Tool** is a lightweight, cross-platform utility designed for automated system auditing and reporting. Built with Python, it provides a unified solution for collecting essential system metrics and configuration data across Windows, Linux, and macOS environments.

The tool is engineered to run as a standalone script or a scheduled task, maintaining a historical record of all audits in a local JSON database. This makes it ideal for tracking system state changes over time, auditing user access, and monitoring resource utilization.

## Key Features

### 🖥️ Comprehensive System Profiling
Gathers detailed hardware and operating system specifications:
- **Host Details**: Hostname, IP Address, MAC Address
- **Hardware**: Processor type, Architecture, Total RAM
- **OS**: Operating System version and release

### 💽 Resource & Storage Monitoring
- Analyzes disk usage across all partitions and mount points
- Reports total size, free space, and usage percentage
- Helps identify storage bottlenecks or capacity issues

### 🛡️ Security & Access Auditing
- Tracks currently logged-in users
- Records login times to monitor session activity
- Useful for detecting unauthorized access or idle sessions

### 📦 Software Inventory
- Generates a complete list of installed applications
- Supports package managers across different OS families:
    - **Windows**: WMIC product list
    - **Linux**: dpkg / rpm
    - **macOS**: System Profiler

### 📊 Data Persistence & History
- **JSON-based Storage**: All reports are appended to `system_reports.json`
- **Run Logging**: Tracks execution frequency and timestamps in `run_log.json`
- **Zero Database Dependency**: No external database setup required

## Technical Specifications
- **Language**: Python 3
- **Dependencies**: `getmac` (for MAC address retrieval)
- **Standard Libraries Used**: `platform`, `socket`, `subprocess`, `json`, `datetime`
- **Architecture**: Single-file script (`system_audit.py`) with modular collection functions

## Use Cases
- **IT Asset Management**: Quickly gather specs for inventory tracking.
- **Server Health Checks**: Monitor disk space and uptime indicators via cron jobs.
- **Security Compliance**: Audit installed software and user access logs.
