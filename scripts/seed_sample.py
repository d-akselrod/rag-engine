"""CLI utility to ingest documents or files into the RAG vector database."""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()

from src.database import SessionLocal
from src.services.rag import rag_service


def seed_file(file_path: Path, document_id: str = None, chunk_size: int = 1000, chunk_overlap: int = 150):
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc_id = document_id or file_path.stem
    print(f"Ingesting '{file_path.name}' ({len(text)} chars) with auto-chunking...")

    db = SessionLocal()
    try:
        chunk_ids = rag_service.add_document(
            db=db,
            content=text,
            document_id=doc_id,
            metadata={"source": file_path.name, "bytes": len(text)},
            auto_chunk=True,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        print(f"[OK] Successfully ingested {len(chunk_ids)} chunk(s) (IDs: {chunk_ids[:5]}...)")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Seed documents into pgvector knowledge base.")
    parser.add_argument("--file", type=Path, help="Path to text or markdown file to ingest")
    parser.add_argument("--id", type=str, default=None, help="Document ID (defaults to filename)")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Target chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=150, help="Chunk overlap in characters")

    args = parser.parse_args()

    if args.file:
        seed_file(args.file, document_id=args.id, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    else:
        from scripts.init_db import seed_sample_data
        seed_sample_data()


if __name__ == "__main__":
    main()
