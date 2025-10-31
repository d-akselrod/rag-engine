"""Alternative setup: Install PostgreSQL locally without Docker."""
import subprocess
import sys
import os
from pathlib import Path

def check_chocolatey():
    """Check if Chocolatey is installed."""
    try:
        result = subprocess.run(['choco', '--version'], 
                              capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except:
        return False, None

def install_postgresql_choco():
    """Install PostgreSQL using Chocolatey."""
    print("\n[INFO] Installing PostgreSQL using Chocolatey...")
    try:
        subprocess.run(['choco', 'install', 'postgresql', '-y'], check=True)
        print("[OK] PostgreSQL installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Installation failed: {e}")
        return False

def install_postgresql_manual():
    """Provide manual installation instructions."""
    print("\n[MANUAL INSTALLATION REQUIRED]")
    print("=" * 70)
    print("\n1. Download PostgreSQL:")
    print("   Visit: https://www.postgresql.org/download/windows/")
    print("   Or use: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads")
    print("\n2. Run the installer:")
    print("   - Use default installation path")
    print("   - Remember the password you set for 'postgres' user")
    print("   - Use default port: 5432")
    print("\n3. After installation, update your .env file:")
    print("   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ragdb")
    print("\n4. Install pgvector extension:")
    print("   a. Download from: https://github.com/pgvector/pgvector/releases")
    print("   b. Copy pgvector.dll to PostgreSQL lib folder")
    print("   c. Copy pgvector.control and pgvector--*.sql to PostgreSQL share/extension folder")
    print("   d. Or use: CREATE EXTENSION vector; (if available)")
    print("\n5. Create database:")
    print("   psql -U postgres")
    print("   CREATE DATABASE ragdb;")
    print("   \\c ragdb")
    print("   CREATE EXTENSION vector;")
    print("\n6. Then run:")
    print("   python scripts/init_db.py")
    print("=" * 70)

def setup_local_postgres():
    """Set up local PostgreSQL."""
    print("=" * 70)
    print("Local PostgreSQL Setup (No Docker Required)")
    print("=" * 70)
    
    # Check if PostgreSQL is already installed
    print("\n[1] Checking for existing PostgreSQL installation...")
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] PostgreSQL is already installed: {result.stdout.strip()}")
        print("\n[INFO] Please ensure:")
        print("  1. PostgreSQL service is running")
        print("  2. You have created database 'ragdb'")
        print("  3. pgvector extension is installed")
        print("  4. Your .env file has correct DATABASE_URL")
        return True
    except:
        print("[INFO] PostgreSQL not found")
    
    # Try Chocolatey installation
    choco_available, choco_version = check_chocolatey()
    if choco_available:
        print(f"\n[2] Chocolatey found: {choco_version}")
        response = input("\nInstall PostgreSQL using Chocolatey? (y/n): ")
        if response.lower() == 'y':
            if install_postgresql_choco():
                print("\n[SUCCESS] PostgreSQL installed!")
                print("\nNext steps:")
                print("1. Start PostgreSQL service")
                print("2. Create database: CREATE DATABASE ragdb;")
                print("3. Update .env file with your password")
                print("4. Run: python scripts/init_db.py")
                return True
    
    # Manual installation
    print("\n[2] Manual installation required")
    install_postgresql_manual()
    return False

if __name__ == "__main__":
    setup_local_postgres()

