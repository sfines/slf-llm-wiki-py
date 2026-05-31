import pytest

from src.core.hashing import generate_short_hash


class TestIdempotency:
    @pytest.mark.asyncio
    async def test_short_hash_consistent_across_runs(self, tmp_path):
        content = "Test content for consistent hashing"

        hash1 = generate_short_hash(content)
        hash2 = generate_short_hash(content)
        hash3 = generate_short_hash(content)

        assert hash1 == hash2 == hash3
        assert len(hash1) == 8
        assert all(c in "0123456789abcdef" for c in hash1)

    def test_hash_normalization_ensures_idempotency(self):
        from src.core.hashing import compute_content_hash

        content_windows = "line1\r\nline2\r\nline3"
        content_unix = "line1\nline2\nline3"
        content_old_mac = "line1\rline2\rline3"

        hash_windows = compute_content_hash(content_windows)
        hash_unix = compute_content_hash(content_unix)
        hash_old_mac = compute_content_hash(content_old_mac)

        assert hash_windows == hash_unix == hash_old_mac

    def test_different_content_different_hash(self):
        from src.core.hashing import compute_content_hash

        content1 = "Content A"
        content2 = "Content B"
        content3 = "Content C"

        hash1 = compute_content_hash(content1)
        hash2 = compute_content_hash(content2)
        hash3 = compute_content_hash(content3)

        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3

    def test_idempotent_filename_generation(self):
        from src.core.hashing import generate_short_hash

        entity_slug = "manuals"
        content = "User manual content"

        short_hash = generate_short_hash(content)
        filename = f"{entity_slug}-{short_hash}.md"

        assert filename.startswith("manuals-")
        assert filename.endswith(".md")
        assert len(filename) == len("manuals-") + 8 + len(".md")

        short_hash2 = generate_short_hash(content)
        filename2 = f"{entity_slug}-{short_hash2}.md"

        assert filename == filename2
