"""Check virtualization status and provide guidance."""
import subprocess
import sys

def check_virtualization():
    """Check virtualization status."""
    print("=" * 70)
    print("Virtualization Status Check")
    print("=" * 70)
    
    # Check Hyper-V
    print("\n[1] Checking Hyper-V...")
    try:
        result = subprocess.run(['systeminfo'], capture_output=True, text=True, check=True)
        if 'Hyper-V' in result.stdout:
            lines = [l for l in result.stdout.split('\n') if 'Hyper-V' in l]
            for line in lines[:3]:
                print(f"  {line.strip()}")
    except Exception as e:
        print(f"  Could not check: {e}")
    
    # Check WSL
    print("\n[2] Checking WSL (Windows Subsystem for Linux)...")
    try:
        result = subprocess.run(['wsl', '--status'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  {result.stdout.strip()}")
        else:
            print("  WSL is not installed or not available")
            print("  Install with: wsl --install")
    except Exception as e:
        print(f"  WSL not available: {e}")
    
    # Check BIOS virtualization
    print("\n[3] Checking BIOS Virtualization Support...")
    try:
        result = subprocess.run(['powershell', '-Command', 
                                'Get-WmiObject Win32_Processor | Select-Object VirtualizationFirmwareEnabled'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
            if 'True' in output:
                print("  [OK] Virtualization is enabled in BIOS")
            elif 'False' in output:
                print("  [FAIL] Virtualization is DISABLED in BIOS")
                print("  You need to enable it in BIOS/UEFI settings")
            else:
                print(f"  {output}")
    except Exception as e:
        print(f"  Could not check: {e}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    print("\nIf virtualization is disabled:")
    print("1. Restart your computer")
    print("2. Enter BIOS/UEFI (usually F2, F10, F12, or Del)")
    print("3. Enable Virtualization Technology (VT-x or AMD-V)")
    print("4. Save and restart")
    print("\nAlternatively, use local PostgreSQL instead of Docker:")
    print("  See VIRTUALIZATION_SETUP.md for instructions")

if __name__ == "__main__":
    check_virtualization()

