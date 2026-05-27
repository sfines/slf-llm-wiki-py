from src.models.document import RawFile, ParsedDocument
from src.core.nodes import parser_node

def test_parser_node(tmp_path):
    # Setup
    test_file = tmp_path / "test.md"
    test_file.write_text("---\ntitle: Test\n---\nHello World")
    
    raw = RawFile(source_path=test_file, entity_type_slug="test_slug")
    
    # Execute
    event = parser_node(raw)
    parsed: ParsedDocument = event.output
    
    # Assert
    assert parsed.entity_type_slug == "test_slug"
    assert parsed.frontmatter == {"title": "Test"}
    assert parsed.body == "Hello World"
