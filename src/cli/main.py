import asyncio
import argparse
from pathlib import Path
import sys

from src.models.config import load_config
from src.core.pipeline import WikiPipeline

async def async_main():
    parser = argparse.ArgumentParser(description="SLF LLM Wiki - CLI Ingestion")
    parser.add_argument(
        "--config", 
        type=str, 
        required=True, 
        help="Path to the config.py file."
    )
    
    args = parser.parse_args()
    
    config_path = Path(args.config)
    
    if not config_path.exists() or not config_path.is_file():
        print(f"Error: Config file '{config_path}' does not exist.")
        sys.exit(1)
        
    print(f"Loading config from '{config_path}'")
    config = load_config(config_path)
    
    print(f"Starting ingestion from '{config.content_dir}' to '{config.wiki_dir}'")
    
    pipeline = WikiPipeline(config=config)
    await pipeline.generate_pages()
    
    print("\nIngestion Complete!")
    
    # Generate Index/Taxonomy
    print("Generating index.md taxonomy...")
    await pipeline.build_index()
    
    print(f"Taxonomy built at: {config.wiki_dir / 'index.md'}")
    print("Run the chat interface to query your new wiki.")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
