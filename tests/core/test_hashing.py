
from src.core.hashing import compute_content_hash, generate_short_hash, normalize_content


class TestNormalizeContent:
    def test_normalizes_crlf_to_lf(self):
        content = "line1\r\nline2\r\nline3"
        result = normalize_content(content)
        assert result == "line1\nline2\nline3"
        assert "\r\n" not in result

    def test_normalizes_cr_to_lf(self):
        content = "line1\rline2\rline3"
        result = normalize_content(content)
        assert result == "line1\nline2\nline3"
        assert "\r" not in result

    def test_enforces_utf8_encoding(self):
        content = "Hello 世界 🌍"
        result = normalize_content(content)
        assert result == "Hello 世界 🌍"

    def test_handles_mixed_line_endings(self):
        content = "line1\r\nline2\nline3\rline4"
        result = normalize_content(content)
        assert result == "line1\nline2\nline3\nline4"

    def test_empty_string_returns_empty(self):
        result = normalize_content("")
        assert result == ""

    def test_preserves_existing_lf(self):
        content = "line1\nline2\nline3"
        result = normalize_content(content)
        assert result == "line1\nline2\nline3"


class TestComputeContentHash:
    def test_produces_sha256_hash(self):
        content = "test content"
        result = compute_content_hash(content)
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in result)

    def test_is_deterministic(self):
        content = "deterministic test"
        hash1 = compute_content_hash(content)
        hash2 = compute_content_hash(content)
        assert hash1 == hash2

    def test_normalizes_before_hashing(self):
        content1 = "line1\r\nline2"
        content2 = "line1\nline2"
        hash1 = compute_content_hash(content1)
        hash2 = compute_content_hash(content2)
        assert hash1 == hash2

    def test_different_content_produces_different_hash(self):
        hash1 = compute_content_hash("content one")
        hash2 = compute_content_hash("content two")
        assert hash1 != hash2

    def test_empty_content_produces_consistent_hash(self):
        hash1 = compute_content_hash("")
        hash2 = compute_content_hash("")
        assert hash1 == hash2
        assert len(hash1) == 64


class TestGenerateShortHash:
    def test_produces_8_char_hash(self):
        content = "test content"
        result = generate_short_hash(content)
        assert isinstance(result, str)
        assert len(result) == 8
        assert all(c in "0123456789abcdef" for c in result)

    def test_is_deterministic(self):
        content = "deterministic short"
        hash1 = generate_short_hash(content)
        hash2 = generate_short_hash(content)
        assert hash1 == hash2

    def test_is_prefix_of_full_hash(self):
        content = "test prefix"
        short = generate_short_hash(content)
        full = compute_content_hash(content)
        assert full.startswith(short)

    def test_different_content_produces_different_short_hash(self):
        hash1 = generate_short_hash("content one")
        hash2 = generate_short_hash("content two")
        assert hash1 != hash2

    def test_normalizes_before_generating(self):
        content1 = "line1\r\nline2"
        content2 = "line1\nline2"
        hash1 = generate_short_hash(content1)
        hash2 = generate_short_hash(content2)
        assert hash1 == hash2
