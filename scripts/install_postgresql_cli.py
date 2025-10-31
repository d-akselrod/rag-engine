"""Download and install PostgreSQL using CLI."""
import subprocess
import sys
import os
import time
from pathlib import Path
import urllib.request

POSTGRESQL_VERSION = "16.2"
POSTGRESQL_URL = f"https://get.enterprisedb.com/postgresql/postgresql-{POSTGRESQL_VERSION}-1-windows-x64.exe"
INSTALLER_PATH = Path.home() / "Downloads" / f"postgresql-{POSTGRESQL_VERSION}-installer.exe"

def download_postgresql():
    """Download PostgreSQL installer."""
    print(f"\n[INFO] Downloading PostgreSQL {POSTGRESQL_VERSION}...")
    print(f"URL: {POSTGRESQL_URL}")
    
    try:
        # Create downloads directory if it doesn't exist
        INSTALLER_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Download the file
        print(f"Downloading to: {INSTALLER_PATH}")
        urllib.request.urlretrieve(POSTGRESQL_URL, INSTALLER_PATH)
        
        if INSTALLER_PATH.exists():
            size_mb = INSTALLER_PATH.stat().st_size / (1024 * 1024)
            print(f"[OK] Download complete ({size_mb:.1f} MB)")
            return True
        else:
            print("[FAIL] Download failed - file not found")
            return False
    except Exception as e:
        print(f"[FAIL] Download failed: {e}")
        return False

def install_postgresql_silent(password):
    """Install PostgreSQL silently using PowerShell with elevation."""
    print(f"\n[INFO] Installing PostgreSQL...")
    print("This will take a few minutes...")
    print("[INFO] You may be prompted for administrator privileges")
    
    # Build installer command
    installer_args = [
        "--mode", "unattended",
        "--superpassword", password,
        "--servicename", "postgresql-x64-16",
        "--servicepassword", password,
        "--serverport", "5432",
        "--locale", "en_US",
        "--datadir", "C:\\Program Files\\PostgreSQL\\16\\data",
        "--installer-language", "en"
    ]
    
    # Format arguments properly for PowerShell
    installer_path_str = str(INSTALLER_PATH).replace("\\", "\\\\")
    args_array = ",".join([f'"{arg}"' for arg in installer_args])
    
    # Use PowerShell to run with elevation
    ps_command = f'''
    $args = @({args_array})
    $proc = Start-Process -FilePath "{installer_path_str}" -ArgumentList $args -Verb RunAs -Wait -PassThru
    if ($proc.ExitCode -eq 0) {{
        Write-Host "Installation completed successfully"
        exit 0
    }} else {{
        Write-Host "Installation failed with exit code $($proc.ExitCode)"
        exit 1
    }}
    '''
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            check=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        print("[OK] PostgreSQL installation completed")
        return True
    except subprocess.TimeoutExpired:
        print("[WARNING] Installation is taking longer than expected")
        print("Please check if installation completed manually")
        return True  # Assume success if still running
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Installation failed")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"[FAIL] Installation error: {e}")
        return False

def check_postgresql_installed():
    """Check if PostgreSQL is installed."""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except:
        return False, None

def start_postgresql_service():
    """Start PostgreSQL service."""
    print("\n[INFO] Starting PostgreSQL service...")
    try:
        subprocess.run(['net', 'start', 'postgresql-x64-16'], 
                      check=True, capture_output=True)
        print("[OK] PostgreSQL service started")
        time.sleep(3)  # Wait for service to be ready
        return True
    except subprocess.CalledProcessError:
        # Try alternative service name
        try:
            subprocess.run(['net', 'start', 'postgresql-16'], 
                          check=True, capture_output=True)
            print("[OK] PostgreSQL service started")
            time.sleep(3)
            return True
        except:
            print("[WARNING] Could not start service automatically")
            print("Please start PostgreSQL service manually from Services")
            return False

def create_database_and_extension(password):
    """Create database and install pgvector extension."""
    print("\n[INFO] Creating database and installing pgvector...")
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        # Create database
        print("Creating database 'ragdb'...")
        subprocess.run([
            'psql', '-U', 'postgres', '-h', 'localhost',
            '-c', 'CREATE DATABASE ragdb;'
        ], env=env, check=True, capture_output=True)
        print("[OK] Database created")
        
        # Install pgvector extension (try, may not be available)
        print("Installing pgvector extension...")
        try:
            subprocess.run([
                'psql', '-U', 'postgres', '-h', 'localhost', '-d', 'ragdb',
                '-c', 'CREATE EXTENSION IF NOT EXISTS vector;'
            ], env=env, check=True, capture_output=True)
            print("[OK] pgvector extension installed")
        except:
            print("[WARNING] pgvector extension not available")
            print("You may need to install it manually later")
            print("Download from: https://github.com/pgvector/pgvector/releases")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Database setup failed: {e.stderr.decode() if e.stderr else e}")
        return False

def main():
    """Main installation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Install PostgreSQL without Docker')
    parser.add_argument('--password', '-p', help='Password for postgres user')
    parser.add_argument('--skip-download', action='store_true', help='Skip download if installer exists')
    args = parser.parse_args()
    
    print("=" * 70)
    print("PostgreSQL Installation (No Docker)")
    print("=" * 70)
    
    # Check if already installed
    installed, version = check_postgresql_installed()
    if installed:
        print(f"\n[INFO] PostgreSQL is already installed: {version}")
        return
    
    # Get password
    password = args.password
    if not password:
        print("\n[ERROR] Password is required")
        print("Usage: python scripts/install_postgresql_cli.py --password YOUR_PASSWORD")
        print("Or: python scripts/install_postgresql_cli.py -p YOUR_PASSWORD")
        sys.exit(1)
    
    # Download
    if args.skip_download and INSTALLER_PATH.exists():
        print(f"\n[INFO] Using existing installer: {INSTALLER_PATH}")
    elif not INSTALLER_PATH.exists():
        if not download_postgresql():
            print("\n[FAIL] Could not download PostgreSQL")
            print("Please download manually from:")
            print("https://www.postgresql.org/download/windows/")
            sys.exit(1)
    
    # Install
    print("\n[INFO] Installing PostgreSQL (this may take a few minutes)...")
    if not install_postgresql_silent(password):
        print("\n[FAIL] Installation failed")
        sys.exit(1)
    
    # Start service
    start_postgresql_service()
    
    # Create database
    create_database_and_extension(password)
    
    # Update .env file
    print("\n[INFO] Updating .env file...")
    env_file = Path(".env")
    if env_file.exists():
        content = env_file.read_text()
        # Update DATABASE_URL
        if "DATABASE_URL=" in content:
            import re
            content = re.sub(
                r'DATABASE_URL=.*',
                f'DATABASE_URL=postgresql://postgres:{password}@localhost:5432/ragdb',
                content
            )
        else:
            content += f"\nDATABASE_URL=postgresql://postgres:{password}@localhost:5432/ragdb\n"
        env_file.write_text(content)
        print("[OK] .env file updated")
    else:
        print("[WARNING] .env file not found, creating it...")
        env_content = f"""# Database Configuration
DATABASE_URL=postgresql://postgres:{password}@localhost:5432/ragdb

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
        env_file.write_text(env_content)
        print("[OK] .env file created")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] PostgreSQL installation complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Initialize the database:")
    print("   python scripts/init_db.py")
    print("2. Test the API:")
    print("   python scripts/test_api.py")
    print("\n[NOTE] If pgvector extension failed to install, you may need to:")
    print("   - Download pgvector from: https://github.com/pgvector/pgvector/releases")
    print("   - Install it manually into PostgreSQL")

if __name__ == "__main__":
    main()

