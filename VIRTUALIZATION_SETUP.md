# Docker Virtualization Setup Guide

Docker Desktop requires virtualization to be enabled on your system. Here's how to fix it:

## Option 1: Enable Virtualization in BIOS/UEFI (Recommended)

1. **Restart your computer**
2. **Enter BIOS/UEFI settings** (usually F2, F10, F12, or Del during boot)
3. **Find Virtualization settings** (may be called):
   - Intel Virtualization Technology (Intel VT-x)
   - AMD-V
   - SVM Mode
   - Virtualization Technology
4. **Enable it**
5. **Save and exit**
6. **Restart Windows**

## Option 2: Enable Windows Features

Run PowerShell as Administrator and execute:

```powershell
# Enable Hyper-V (if available)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All

# Enable WSL2 (Windows Subsystem for Linux)
wsl --install

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Enable Windows Hypervisor Platform
dism.exe /online /enable-feature /featurename:HypervisorPlatform /all /norestart
```

Then restart your computer.

## Option 3: Use Local PostgreSQL Instead (No Docker Needed)

If you can't enable virtualization, you can install PostgreSQL directly:

### Quick Install via Chocolatey (if installed):
```powershell
choco install postgresql
```

### Manual Install:
1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Install with default settings
3. Remember the password you set for the `postgres` user
4. Install pgvector extension:
   - Download from: https://github.com/pgvector/pgvector/releases
   - Or use: `CREATE EXTENSION vector;` after installation

Then update your `.env` file:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ragdb
```

## Check Current Status

Run these commands to check your virtualization status:

```powershell
# Check Hyper-V status
systeminfo | Select-String "Hyper-V"

# Check virtualization in BIOS
Get-WmiObject Win32_Processor | Select-Object VirtualizationFirmwareEnabled

# Check WSL status
wsl --status
```

## After Enabling Virtualization

1. Restart your computer
2. Start Docker Desktop
3. Wait for it to fully start (whale icon in system tray)
4. Run: `python scripts/setup_docker.py`
5. Initialize database: `python scripts/init_db.py`
6. Test: `python scripts/test_api.py`

