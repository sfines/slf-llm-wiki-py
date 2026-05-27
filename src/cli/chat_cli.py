import argparse
import sys
from pathlib import Path
from src.models.config import load_config
from src.ui.chat import WikiChatApp

def main():
    parser = argparse.ArgumentParser(description="SLF LLM Wiki - Web Chat")
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
        
    config = load_config(config_path)
    
    app = WikiChatApp(config)
    app.run()

if __name__ == "__main__":
    main()
