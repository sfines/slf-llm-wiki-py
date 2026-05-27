import re
import hashlib

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
    # Remove frontmatter
    text = remove_frontmatter(text)
    
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Remove inline code
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove images
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    
    # Remove bold, italics, strikethrough
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
    text = re.sub(r'(~~)(.*?)\1', r'\2', text)
    
    # Remove headings (keep the text)
    text = re.sub(r'^\s*#+\s+(.*)', r'\1', text, flags=re.MULTILINE)
    
    # Remove blockquotes
    text = re.sub(r'^\s*>\s+(.*)', r'\1', text, flags=re.MULTILINE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def generate_content_hash(text: str) -> str:
    """Generates a deterministic SHA-256 hash from the stripped text."""
    stripped_text = md_strip(text)
    return hashlib.sha256(stripped_text.encode("utf-8")).hexdigest()

def generate_content_uuid(text: str) -> str:
    """Generates a deterministic UUID-like string based on content hash."""
    import uuid
    hash_hex = generate_content_hash(text)
    # Use first 32 chars of sha256 to create a deterministic UUID
    return str(uuid.UUID(hash_hex[:32]))
