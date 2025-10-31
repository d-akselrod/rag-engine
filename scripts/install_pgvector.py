"""Download and install pgvector extension for PostgreSQL."""
import subprocess
import sys
import os
import urllib.request
import zipfile
from pathlib import Path

PG_BIN_PATH = r"C:\Program Files\PostgreSQL\18\bin"
PG_DATA_PATH = r"C:\Program Files\PostgreSQL\18"
PG_LIB_PATH = os.path.join(PG_DATA_PATH, "lib")
PG_SHARE_PATH = os.path.join(PG_DATA_PATH, "share", "extension")

PGVECTOR_VERSION = "0.5.1"
PGVECTOR_URL = f"https://github.com/pgvector/pgvector/archive/refs/tags/v{PGVECTOR_VERSION}.zip"

def download_pgvector():
    """Download pgvector source."""
    print(f"\n[INFO] Downloading pgvector v{PGVECTOR_VERSION}...")
    zip_path = Path.home() / "Downloads" / f"pgvector-{PGVECTOR_VERSION}.zip"
    
    try:
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(PGVECTOR_URL, zip_path)
        print(f"[OK] Downloaded to: {zip_path}")
        return zip_path
    except Exception as e:
        print(f"[FAIL] Download failed: {e}")
        return None

def build_pgvector(zip_path):
    """Build pgvector from source."""
    print("\n[INFO] Building pgvector...")
    print("[WARNING] Building pgvector requires:")
    print("  - Visual Studio Build Tools")
    print("  - PostgreSQL development headers")
    print("\n[RECOMMENDATION] Use pre-built binaries instead:")
    print("  1. Download from: https://github.com/pgvector/pgvector/releases")
    print("  2. For PostgreSQL 18, download: pgvector-0.5.1-pg18-windows-x64.zip")
    print("  3. Extract and copy files:")
    print("     - pgvector.dll -> C:\\Program Files\\PostgreSQL\\18\\lib")
    print("     - pgvector.control -> C:\\Program Files\\PostgreSQL\\18\\share\\extension")
    print("     - pgvector--*.sql -> C:\\Program Files\\PostgreSQL\\18\\share\\extension")
    return False

def install_pgvector_binary():
    """Provide instructions for manual installation."""
    print("\n" + "=" * 70)
    print("pgvector Installation Instructions")
    print("=" * 70)
    print("\n1. Download pgvector for PostgreSQL 18:")
    print("   https://github.com/pgvector/pgvector/releases")
    print("   Look for: pgvector-0.5.1-pg18-windows-x64.zip")
    print("\n2. Extract the zip file")
    print("\n3. Copy files to PostgreSQL directory:")
    print(f"   - Copy pgvector.dll to: {PG_LIB_PATH}")
    print(f"   - Copy pgvector.control to: {PG_SHARE_PATH}")
    print(f"   - Copy pgvector--*.sql to: {PG_SHARE_PATH}")
    print("\n4. Then run: python scripts/init_db.py")
    print("=" * 70)
    
    # Try to download the binary release
    print("\n[INFO] Attempting to download pre-built binary...")
    binary_url = "https://github.com/pgvector/pgvector/releases/download/v0.5.1/pgvector-0.5.1-pg18-windows-x64.zip"
    zip_path = Path.home() / "Downloads" / "pgvector-pg18-windows-x64.zip"
    
    try:
        print(f"Downloading from: {binary_url}")
        urllib.request.urlretrieve(binary_url, zip_path)
        print(f"[OK] Downloaded to: {zip_path}")
        
        # Extract
        print("\n[INFO] Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(Path.home() / "Downloads" / "pgvector")
        
        extract_dir = Path.home() / "Downloads" / "pgvector"
        print(f"[OK] Extracted to: {extract_dir}")
        print("\n[ACTION REQUIRED] Copy files manually:")
        print(f"  From: {extract_dir}")
        print(f"  To: {PG_DATA_PATH}")
        print("\nOr run this PowerShell command (as Administrator):")
        print(f"  Copy-Item '{extract_dir}\\lib\\pgvector.dll' '{PG_LIB_PATH}\\'")
        print(f"  Copy-Item '{extract_dir}\\share\\extension\\pgvector.*' '{PG_SHARE_PATH}\\'")
        
        return True
    except Exception as e:
        print(f"[FAIL] Could not download binary: {e}")
        print("Please download manually from GitHub releases")
        return False

def main():
    """Main function."""
    print("=" * 70)
    print("pgvector Extension Installation")
    print("=" * 70)
    
    # Check if already installed
    env = os.environ.copy()
    env['PGPASSWORD'] = 'ragpass123'
    
    try:
        result = subprocess.run([
            os.path.join(PG_BIN_PATH, "psql.exe"), '-U', 'postgres', '-h', 'localhost', '-d', 'ragdb',
            '-c', "SELECT * FROM pg_available_extensions WHERE name = 'vector';"
        ], env=env, capture_output=True, text=True, timeout=5)
        
        if 'vector' in result.stdout.lower():
            print("[OK] pgvector extension is already available!")
            return
    except:
        pass
    
    install_pgvector_binary()

if __name__ == "__main__":
    main()

