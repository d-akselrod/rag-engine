"""Setup script for Docker Desktop and PostgreSQL."""
import subprocess
import sys
import os
import time
from pathlib import Path

def check_docker():
    """Check if Docker is installed."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None

def check_docker_running():
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, check=True)
        return True
    except:
        return False

def install_docker_desktop_windows():
    """Provide instructions for installing Docker Desktop on Windows."""
    print("\n[Docker Desktop Installation Required]")
    print("=" * 70)
    print("\nDocker Desktop needs to be installed manually on Windows.")
    print("\nOption 1: Download and Install Docker Desktop")
    print("  1. Visit: https://www.docker.com/products/docker-desktop/")
    print("  2. Download Docker Desktop for Windows")
    print("  3. Run the installer")
    print("  4. Restart your computer if prompted")
    print("  5. Start Docker Desktop from the Start menu")
    print("  6. Wait for Docker to start (whale icon in system tray)")
    print("\nOption 2: Use Winget (Windows Package Manager)")
    print("  Run: winget install Docker.DockerDesktop")
    print("\nAfter installation, run this script again.")
    print("=" * 70)
    return False

def start_postgres():
    """Start PostgreSQL using Docker Compose."""
    compose_file = Path(__file__).parent.parent / "docker-compose.yml"
    
    if not compose_file.exists():
        print(f"[ERROR] docker-compose.yml not found at {compose_file}")
        return False
    
    print("\n[INFO] Starting PostgreSQL container...")
    try:
        # Check if container already exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=rag-engine-postgres', '--format', '{{.Names}}'],
                              capture_output=True, text=True)
        
        if 'rag-engine-postgres' in result.stdout:
            print("[INFO] Container exists, starting it...")
            subprocess.run(['docker', 'start', 'rag-engine-postgres'], check=True)
        else:
            print("[INFO] Creating and starting container...")
            subprocess.run(['docker', 'compose', '-f', str(compose_file), 'up', '-d'], check=True)
        
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
            print("[FAIL] PostgreSQL container is not running")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Error starting PostgreSQL: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 70)
    print("RAG Engine - Docker & PostgreSQL Setup")
    print("=" * 70)
    
    # Check Docker installation
    docker_installed, docker_version = check_docker()
    
    if not docker_installed:
        print("\n[STEP 1] Docker is not installed")
        if sys.platform == "win32":
            install_docker_desktop_windows()
            return
        else:
            print("Please install Docker first.")
            return
    
    print(f"\n[STEP 1] Docker is installed: {docker_version}")
    
    # Check if Docker is running
    if not check_docker_running():
        print("\n[STEP 2] Docker daemon is not running")
        print("Please start Docker Desktop and wait for it to be ready.")
        print("Look for the Docker whale icon in your system tray.")
        return
    
    print("[STEP 2] Docker daemon is running")
    
    # Start PostgreSQL
    print("\n[STEP 3] Starting PostgreSQL...")
    if start_postgres():
        print("\n[SUCCESS] PostgreSQL is running!")
        print("\nNext steps:")
        print("1. Initialize the database:")
        print("   python scripts/init_db.py")
        print("2. Test the API:")
        print("   python scripts/test_api.py")
    else:
        print("\n[FAIL] Failed to start PostgreSQL")
        print("Check Docker logs: docker logs rag-engine-postgres")

if __name__ == "__main__":
    main()

