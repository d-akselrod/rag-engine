"""Set up PostgreSQL database non-interactively."""
import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

PG_BIN_PATH = r"C:\Program Files\PostgreSQL\18\bin"
PG_PSQL = os.path.join(PG_BIN_PATH, "psql.exe")

def setup_database(password):
    """Set up database and pgvector extension."""
    print("\n[1] Setting up database...")
    
    # Set PGPASSWORD environment variable
    env = os.environ.copy()
    env['PGPASSWORD'] = password
    
    try:
        # Create database
        print("Creating database 'ragdb'...")
        result = subprocess.run([
            PG_PSQL, '-U', 'postgres', '-h', 'localhost',
            '-c', 'CREATE DATABASE ragdb;'
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0 or 'already exists' in result.stderr.lower():
            print("[OK] Database 'ragdb' ready")
        else:
            if 'already exists' not in result.stderr.lower():
                print(f"[INFO] {result.stderr.strip()}")
        
        # Install pgvector extension
        print("Installing pgvector extension...")
        result = subprocess.run([
            PG_PSQL, '-U', 'postgres', '-h', 'localhost', '-d', 'ragdb',
            '-c', 'CREATE EXTENSION IF NOT EXISTS vector;'
        ], env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] pgvector extension installed")
            return True
        else:
            error_msg = result.stderr.lower()
            if 'could not open extension control file' in error_msg or 'extension "vector" does not exist' in error_msg:
                print("[WARNING] pgvector extension not available")
                print("The database will work but vector search won't function.")
                print("To install pgvector:")
                print("  1. Download from: https://github.com/pgvector/pgvector/releases")
                print("  2. Copy files to PostgreSQL installation directory")
                return False
            else:
                print(f"[WARNING] {result.stderr.strip()}")
                return False
        
    except Exception as e:
        print(f"[FAIL] Database setup error: {e}")
        return False

def update_env_file(password):
    """Update .env file with database URL."""
    print("\n[2] Updating .env file...")
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup PostgreSQL database')
    parser.add_argument('--password', '-p', required=True, help='PostgreSQL postgres user password')
    args = parser.parse_args()
    
    print("=" * 70)
    print("PostgreSQL Database Setup")
    print("=" * 70)
    print(f"\nUsing PostgreSQL at: {PG_BIN_PATH}")
    
    # Setup database
    setup_database(args.password)
    
    # Update .env
    update_env_file(args.password)
    
    print("\n" + "=" * 70)
    print("[SUCCESS] Database setup complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Initialize the database with sample data:")
    print("   python scripts/init_db.py")
    print("2. Test the API:")
    print("   python scripts/test_api.py")

if __name__ == "__main__":
    main()

