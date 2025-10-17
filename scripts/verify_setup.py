"""Environment, database, and dependency verification script."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def check_env():
    env_file = Path(".env")
    if not env_file.exists():
        print("[FAIL] .env file not found. Create one by copying .env.example")
        return False

    from dotenv import load_dotenv
    load_dotenv()

    required = ["DATABASE_URL", "GEMINI_API_KEY"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        print(f"[FAIL] Missing required environment variables: {', '.join(missing)}")
        return False

    print("[PASS] Environment variables configured.")
    return True


def check_dependencies():
    packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pgvector", "pgvector"),
        ("psycopg2", "psycopg2-binary"),
        ("google.generativeai", "Google Generative AI"),
        ("pydantic", "Pydantic"),
    ]
    for mod_name, label in packages:
        try:
            __import__(mod_name)
        except ImportError:
            print(f"[FAIL] Missing package: {label}")
            return False

    print("[PASS] Core dependencies installed.")
    return True


def check_database():
    try:
        from sqlalchemy import text
        from src.database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            res = conn.execute(
                text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            )
            has_vector = res.scalar()
            if not has_vector:
                print("[FAIL] PostgreSQL connected, but vector extension is missing. Run: make db-init")
                return False

        print("[PASS] PostgreSQL connectivity & pgvector extension verified.")
        return True
    except Exception as e:
        print(f"[FAIL] Database connection error: {e}")
        return False


def main():
    print("=== RAG Engine Verification Check ===\n")
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_env),
        ("Database & Vector Extension", check_database),
    ]

    all_passed = True
    for label, fn in checks:
        print(f"Checking {label}...")
        if not fn():
            all_passed = False
        print()

    if all_passed:
        print("=== Status: ALL CHECKS PASSED ===")
        print("Ready to start server: make dev")
    else:
        print("=== Status: ISSUES DETECTED ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
