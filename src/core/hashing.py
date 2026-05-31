import hashlib
import re


def remove_frontmatter(text: str) -> str:
    """Removes YAML/JSON frontmatter from markdown text."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return text.strip()


def md_strip(text: str) -> str:
    """
    Strips markdown formatting to extract raw text for consistent hashing.
    """
    text = remove_frontmatter(text)

    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

    text = re.sub(r"`([^`]+)`", r"\1", text)

    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

    text = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", "", text)

    text = re.sub(r"(\*\*|__)(.*?)\1", r"\2", text)
    text = re.sub(r"(\*|_)(.*?)\1", r"\2", text)
    text = re.sub(r"(~~)(.*?)\1", r"\2", text)

    text = re.sub(r"^\s*#+\s+(.*)", r"\1", text, flags=re.MULTILINE)

    text = re.sub(r"^\s*>\s+(.*)", r"\1", text, flags=re.MULTILINE)

    text = re.sub(r"<[^>]+>", "", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_content(text: str) -> str:
    """
    Normalizes content for consistent hashing.

    - Converts all line endings to LF (\n)
    - Ensures UTF-8 encoding representation
    - Strips leading and trailing whitespace

    Args:
        text: Input text to normalize

    Returns:
        Normalized text with consistent line endings
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n")

    text = text.replace("\r", "\n")

    text = text.encode("utf-8", errors="ignore").decode("utf-8")

    return text.strip()


def compute_content_hash(text: str) -> str:
    """
    Computes a deterministic SHA-256 hash from the given text.

    Normalizes the text before hashing to ensure consistent results
    regardless of line ending style.

    Args:
        text: Input text to hash

    Returns:
        64-character hexadecimal SHA-256 hash string
    """
    normalized = normalize_content(text)
    stripped = md_strip(normalized)
    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()


def generate_short_hash(text: str, length: int = 8) -> str:
    """
    Generates a short hash prefix from the content hash.

    Args:
        text: Input text to hash
        length: Number of characters to return (default: 8)

    Returns:
        First `length` characters of the SHA-256 hash
    """
    full_hash = compute_content_hash(text)
    return full_hash[:length]


def generate_content_uuid(text: str) -> str:
    """
    Generates a deterministic UUID-like string based on content hash.

    Args:
        text: Input text to generate UUID from

    Returns:
        UUID string in standard format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
    """
    import uuid

    hash_hex = compute_content_hash(text)
    return str(uuid.UUID(hash_hex[:32]))
