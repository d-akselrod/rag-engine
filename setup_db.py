"""Quick database setup script."""
import subprocess
import sys
import os
from pathlib import Path

PG_BIN_PATH = r"C:\Program Files\PostgreSQL\18\bin"
PG_PSQL = os.path.join(PG_BIN_PATH, "psql.exe")

def test_connection(password):
    """Test PostgreSQL connection."""
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        result = subprocess.run([
            PG_PSQL, '-U', 'postgres', '-h', 'localhost',
            '-c', 'SELECT version();'
        ], env=env, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            return True
        return False
    except:
        return False

def setup_database(password):
    """Set up database."""
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    print("\n[1] Creating database...")
    result = subprocess.run([
        PG_PSQL, '-U', 'postgres', '-h', 'localhost',
        '-c', 'CREATE DATABASE ragdb;'
    ], env=env, capture_output=True, text=True)
    
    if result.returncode == 0 or 'already exists' in result.stderr.lower():
        print("[OK] Database ready")
    else:
        print(f"[INFO] {result.stderr.strip()}")
    
    print("\n[2] Installing pgvector extension...")
    result = subprocess.run([
        PG_PSQL, '-U', 'postgres', '-h', 'localhost', '-d', 'ragdb',
        '-c', 'CREATE EXTENSION IF NOT EXISTS vector;'
    ], env=env, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[OK] pgvector extension installed")
    else:
        print("[WARNING] pgvector extension not available")
        print("(Database will work but vector search won't function)")
    
    return True

def update_env(password):
    """Update .env file."""
    env_file = Path(".env")
    db_url = f"postgresql://postgres:{password}@localhost:5432/ragdb"
    
    if env_file.exists():
        content = env_file.read_text()
        import re
        if re.search(r'^DATABASE_URL=', content, re.MULTILINE):
            content = re.sub(r'^DATABASE_URL=.*', f'DATABASE_URL={db_url}', content, flags=re.MULTILINE)
        else:
            content += f"\nDATABASE_URL={db_url}\n"
        env_file.write_text(content)
    else:
        env_file.write_text(f"""DATABASE_URL={db_url}
GEMINI_API_KEY=your_gemini_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
""")
    print("[OK] .env file updated")

if __name__ == "__main__":
    print("=" * 70)
    print("PostgreSQL Database Setup")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        password = sys.argv[1]
    else:
        print("\nEnter the password you set for PostgreSQL 'postgres' user:")
        password = input("Password: ")
    
    if not password:
        print("[ERROR] Password required")
        sys.exit(1)
    
    print("\n[INFO] Testing connection...")
    if not test_connection(password):
        print("[FAIL] Connection failed. Please check:")
        print("  1. PostgreSQL service is running")
        print("  2. Password is correct")
        print("  3. Port 5432 is accessible")
        sys.exit(1)
    
    print("[OK] Connection successful!")
    
    setup_database(password)
    update_env(password)
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Setup complete!")
    print("=" * 70)
    print("\nNext: python scripts/init_db.py")

