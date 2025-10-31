"""Script to verify setup and check for common issues."""
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print("[X] .env file not found!")
        print("   Please copy .env.example to .env and configure it.")
        return False
    print("[OK] .env file exists")
    return True


def check_env_variables():
    """Check if required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["DATABASE_URL", "GEMINI_API_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"[X] Missing environment variables: {', '.join(missing)}")
        return False
    
    print("[OK] All required environment variables are set")
    return True


def check_imports():
    """Check if all required modules can be imported."""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import psycopg2
        import google.generativeai
        print("[OK] All required packages are installed")
        return True
    except ImportError as e:
        print(f"[X] Missing package: {e}")
        return False


def check_code_structure():
    """Check if code structure is correct."""
    # Skip if .env doesn't exist since config requires it
    env_path = Path(".env")
    if not env_path.exists():
        print("[SKIP] Code structure check skipped (no .env file)")
        return True
    
    try:
        from src.config import settings
        from src.database import get_db, engine
        from src.models import DocumentChunk
        from src.services import rag_service
        from src.main import app
        print("[OK] Code structure is correct")
        return True
    except Exception as e:
        print(f"[X] Code structure error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks."""
    print("=== RAG Engine Setup Verification ===\n")
    
    checks = [
        ("Package imports", check_imports),
        ("Code structure", check_code_structure),
        (".env file", check_env_file),
        ("Environment variables", check_env_variables),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        result = check_func()
        results.append(result)
    
    print("\n=== Summary ===")
    if all(results):
        print("[OK] All checks passed! You're ready to run the API.")
        print("\nNext steps:")
        print("1. Make sure PostgreSQL is running with pgvector extension")
        print("2. Run: python scripts/init_db.py")
        print("3. Run: uvicorn src.main:app --reload")
    else:
        print("[X] Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

