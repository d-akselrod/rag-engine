"""Recursive text chunking utility for document preparation."""
from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
    separators: List[str] = None,
) -> List[str]:
    """Split text recursively into overlapping chunks respecting natural boundaries.

    Args:
        text: Input text to split.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of characters to overlap between consecutive chunks.
        separators: Priority list of delimiters (default: paragraphs, newlines, sentences, spaces).

    Returns:
        List of non-empty text chunks.
    """
    if not text or not text.strip():
        return []

    text = text.strip()
    if len(text) <= chunk_size:
        return [text]

    if separators is None:
        separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def _split(txt: str, sep_idx: int) -> List[str]:
        if len(txt) <= chunk_size or sep_idx >= len(separators):
            return [txt] if txt.strip() else []

        sep = separators[sep_idx]
        parts = txt.split(sep) if sep else list(txt)

        result: List[str] = []
        current: List[str] = []
        current_len = 0

        for part in parts:
            part_len = len(part) + (len(sep) if current else 0)
            if current and current_len + part_len > chunk_size:
                merged = sep.join(current).strip()
                if merged:
                    if len(merged) > chunk_size and sep_idx + 1 < len(separators):
                        result.extend(_split(merged, sep_idx + 1))
                    else:
                        result.append(merged)

                # Keep overlap from the end of current
                overlap_parts: List[str] = []
                overlap_len = 0
                for p in reversed(current):
                    if overlap_len + len(p) <= chunk_overlap:
                        overlap_parts.insert(0, p)
                        overlap_len += len(p) + len(sep)
                    else:
                        break
                current = overlap_parts
                current_len = sum(len(p) for p in current) + max(0, len(current) - 1) * len(sep)

            current.append(part)
            current_len += len(part) + (len(sep) if len(current) > 1 else 0)

        if current:
            merged = sep.join(current).strip()
            if merged:
                if len(merged) > chunk_size and sep_idx + 1 < len(separators):
                    result.extend(_split(merged, sep_idx + 1))
                else:
                    result.append(merged)

        return result

    return _split(text, 0)
