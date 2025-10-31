"""Alternative PostgreSQL setup without Docker."""
import subprocess
import sys
import os
from pathlib import Path

def check_postgresql_installed():
    """Check if PostgreSQL is installed locally."""
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
    except:
        pass
    
    # Check common installation paths
    common_paths = [
        r"C:\Program Files\PostgreSQL",
        r"C:\Program Files (x86)\PostgreSQL",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return True, f"Found at {path}"
    
    return False, None

def install_postgresql_windows():
    """Provide instructions for installing PostgreSQL on Windows."""
    print("\n[PostgreSQL Installation Required]")
    print("=" * 70)
    print("\nOption 1: Install PostgreSQL using Winget")
    print("  Run: winget install PostgreSQL.PostgreSQL")
    print("\nOption 2: Download from official website")
    print("  1. Visit: https://www.postgresql.org/download/windows/")
    print("  2. Download the installer")
    print("  3. Run the installer")
    print("  4. Remember the password you set for the 'postgres' user")
    print("  5. Default port is 5432")
    print("\nAfter installation, update your .env file with:")
    print("  DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/ragdb")
    print("=" * 70)

def setup_postgresql_database():
    """Create database and enable pgvector extension."""
    print("\n[Setting up PostgreSQL database]")
    print("=" * 70)
    
    # Get database URL from .env
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL not found in .env file")
        return False
    
    print(f"Database URL configured: {db_url.split('@')[1] if '@' in db_url else 'hidden'}")
    
    # Try to connect and create database
    try:
        # Parse database URL
        # Format: postgresql://user:password@host:port/dbname
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        db_name = parsed.path.strip('/') or 'ragdb'
        db_user = parsed.username or 'postgres'
        db_host = parsed.hostname or 'localhost'
        db_port = parsed.port or 5432
        
        print(f"\nCreating database '{db_name}' if it doesn't exist...")
        print(f"Connect to PostgreSQL and run:")
        print(f"  CREATE DATABASE {db_name};")
        print(f"\nThen run:")
        print(f"  python scripts/init_db.py")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("=" * 70)
    print("RAG Engine - PostgreSQL Setup (Without Docker)")
    print("=" * 70)
    
    # Check if PostgreSQL is installed
    installed, info = check_postgresql_installed()
    
    if installed:
        print(f"\n[OK] PostgreSQL is installed: {info}")
        
        # Check if we can connect
        try:
            from src.database import engine
            conn = engine.connect()
            conn.close()
            print("[OK] Can connect to PostgreSQL")
            print("\n[INFO] Running database initialization...")
            print("Run: python scripts/init_db.py")
        except Exception as e:
            print(f"\n[INFO] PostgreSQL is installed but not configured")
            print("Update your .env file with the correct DATABASE_URL")
            setup_postgresql_database()
    else:
        print("\n[INFO] PostgreSQL is not installed")
        install_postgresql_windows()
        print("\nAfter installation, run this script again.")

if __name__ == "__main__":
    main()

