"""Setup PostgreSQL database after manual installation."""
import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def check_postgresql():
    """Check if PostgreSQL is accessible."""
    print("\n[1] Checking PostgreSQL installation...")
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] PostgreSQL found: {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"[FAIL] PostgreSQL not found in PATH")
        print("Please add PostgreSQL bin directory to PATH")
        print("Usually: C:\\Program Files\\PostgreSQL\\16\\bin")
        return False

def check_service():
    """Check if PostgreSQL service is running."""
    print("\n[2] Checking PostgreSQL service...")
    try:
        result = subprocess.run(['powershell', '-Command', 
                                'Get-Service -Name "*postgres*" | Select-Object -ExpandProperty Status'],
                              capture_output=True, text=True)
        if 'Running' in result.stdout:
            print("[OK] PostgreSQL service is running")
            return True
        else:
            print("[WARNING] PostgreSQL service may not be running")
            print("Start it with: net start postgresql-x64-16")
            return False
    except:
        print("[INFO] Could not check service status")
        return True  # Assume it's running

def setup_database(password):
    """Set up database and pgvector extension."""
    print("\n[3] Setting up database...")
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        # Create database
        print("Creating database 'ragdb'...")
        result = subprocess.run([
            'psql', '-U', 'postgres', '-h', 'localhost',
            '-c', 'CREATE DATABASE ragdb;'
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0 or 'already exists' in result.stderr.lower():
            print("[OK] Database 'ragdb' ready")
        else:
            print(f"[WARNING] Database creation: {result.stderr}")
        
        # Install pgvector extension
        print("Installing pgvector extension...")
        result = subprocess.run([
            'psql', '-U', 'postgres', '-h', 'localhost', '-d', 'ragdb',
            '-c', 'CREATE EXTENSION IF NOT EXISTS vector;'
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] pgvector extension installed")
            return True
        else:
            error_msg = result.stderr.lower()
            if 'could not open extension control file' in error_msg or 'extension "vector" does not exist' in error_msg:
                print("[WARNING] pgvector extension not available")
                print("You may need to install it manually:")
                print("  1. Download from: https://github.com/pgvector/pgvector/releases")
                print("  2. Copy files to PostgreSQL installation directory")
                print("  3. Or use: CREATE EXTENSION vector;")
            else:
                print(f"[WARNING] {result.stderr}")
            return False
        
    except Exception as e:
        print(f"[FAIL] Database setup error: {e}")
        return False

def update_env_file(password):
    """Update .env file with database URL."""
    print("\n[4] Updating .env file...")
    env_file = Path(".env")
    
    db_url = f"postgresql://postgres:{password}@localhost:5432/ragdb"
    
    if env_file.exists():
        content = env_file.read_text()
        # Update or add DATABASE_URL
        import re
        if re.search(r'^DATABASE_URL=', content, re.MULTILINE):
            content = re.sub(
                r'^DATABASE_URL=.*',
                f'DATABASE_URL={db_url}',
                content,
                flags=re.MULTILINE
            )
        else:
            content += f"\nDATABASE_URL={db_url}\n"
        env_file.write_text(content)
        print("[OK] .env file updated")
    else:
        print("[INFO] Creating .env file...")
        env_content = f"""# Database Configuration
DATABASE_URL={db_url}

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
        env_file.write_text(env_content)
        print("[OK] .env file created")

def main():
    """Main setup function."""
    print("=" * 70)
    print("PostgreSQL Database Setup")
    print("=" * 70)
    
    # Check installation
    if not check_postgresql():
        print("\n[ACTION REQUIRED]")
        print("Please add PostgreSQL to PATH:")
        print("1. Find PostgreSQL installation (usually C:\\Program Files\\PostgreSQL\\16\\bin)")
        print("2. Add it to PATH environment variable")
        print("3. Restart terminal/PowerShell")
        return
    
    check_service()
    
    # Get password
    import getpass
    print("\n[SETUP] Database Configuration")
    print("Enter the password you set for the 'postgres' user:")
    password = getpass.getpass("Password: ")
    
    if not password:
        print("[FAIL] Password is required")
        return
    
    # Setup database
    setup_database(password)
    
    # Update .env
    update_env_file(password)
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Database setup complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Initialize the database with sample data:")
    print("   python scripts/init_db.py")
    print("2. Test the API:")
    print("   python scripts/test_api.py")
    print("\nNote: If pgvector extension is not installed, the API will")
    print("still work but vector similarity search won't function properly.")

if __name__ == "__main__":
    main()

