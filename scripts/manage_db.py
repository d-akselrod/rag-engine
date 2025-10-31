"""Script to set up local PostgreSQL database using Docker."""
import subprocess
import sys
import time
from pathlib import Path

def check_docker():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] Docker found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[X] Docker not found. Please install Docker Desktop.")
        return False

def check_docker_compose():
    """Check if Docker Compose is available."""
    try:
        # Try docker compose (v2)
        result = subprocess.run(['docker', 'compose', 'version'], 
                              capture_output=True, text=True, check=True)
        print(f"[OK] Docker Compose found: {result.stdout.strip()}")
        return 'docker compose'
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try docker-compose (v1)
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"[OK] Docker Compose found: {result.stdout.strip()}")
            return 'docker-compose'
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[X] Docker Compose not found.")
            return None

def start_postgres():
    """Start PostgreSQL container using Docker Compose."""
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        print("\n[X] Cannot start PostgreSQL: Docker Compose not available")
        return False
    
    if not check_docker():
        return False
    
    docker_compose_file = Path(__file__).parent.parent / "docker-compose.yml"
    if not docker_compose_file.exists():
        print(f"[X] docker-compose.yml not found at {docker_compose_file}")
        return False
    
    print("\n[INFO] Starting PostgreSQL with pgvector...")
    print("       This may take a minute on first run...")
    
    try:
        # Start the container
        cmd = compose_cmd.split() + ['-f', str(docker_compose_file), 'up', '-d']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("[OK] PostgreSQL container started")
        
        # Wait for PostgreSQL to be ready
        print("[INFO] Waiting for PostgreSQL to be ready...")
        time.sleep(5)
        
        # Check if container is running
        result = subprocess.run(['docker', 'ps', '--filter', 'name=rag-engine-postgres', '--format', '{{.Status}}'],
                              capture_output=True, text=True)
        if result.stdout.strip():
            print(f"[OK] PostgreSQL is running: {result.stdout.strip()}")
            return True
        else:
            print("[X] PostgreSQL container is not running")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[X] Error starting PostgreSQL: {e.stderr}")
        return False

def stop_postgres():
    """Stop PostgreSQL container."""
    compose_cmd = check_docker_compose()
    if not compose_cmd:
        return False
    
    docker_compose_file = Path(__file__).parent.parent / "docker-compose.yml"
    if not docker_compose_file.exists():
        return False
    
    print("\n[INFO] Stopping PostgreSQL container...")
    try:
        cmd = compose_cmd.split() + ['-f', str(docker_compose_file), 'down']
        subprocess.run(cmd, check=True)
        print("[OK] PostgreSQL container stopped")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[X] Error stopping PostgreSQL: {e}")
        return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage local PostgreSQL database')
    parser.add_argument('action', choices=['start', 'stop', 'status'], 
                       help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        if start_postgres():
            print("\n=== Setup Complete ===")
            print("Database URL: postgresql://raguser:ragpass@localhost:5432/ragdb")
            print("\nNext steps:")
            print("1. Make sure your .env file has:")
            print("   DATABASE_URL=postgresql://raguser:ragpass@localhost:5432/ragdb")
            print("2. Run: python scripts/init_db.py")
            print("3. Run: uvicorn src.main:app --reload")
        else:
            sys.exit(1)
    
    elif args.action == 'stop':
        stop_postgres()
    
    elif args.action == 'status':
        try:
            result = subprocess.run(['docker', 'ps', '--filter', 'name=rag-engine-postgres', '--format', '{{.Names}} {{.Status}}'],
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print(f"[OK] PostgreSQL is running: {result.stdout.strip()}")
            else:
                print("[X] PostgreSQL container is not running")
        except Exception as e:
            print(f"[X] Error checking status: {e}")

if __name__ == "__main__":
    main()

