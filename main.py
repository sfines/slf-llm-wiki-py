import asyncio
import os
import logging
from pathlib import Path
import click

from src.models.config import load_config
from src.core.pipeline import WikiPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@click.group()
@click.option('--config', default="config/wiki_config.py", type=click.Path(exists=False), help="Path to Python config file")
@click.option('--verbose', is_flag=True, help="Enable detailed logging")
@click.pass_context
def cli(ctx, config: str, verbose: bool):
    """Wiki LLM - ADK Implementation"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    config_path = Path(config)
    if not config_path.exists():
        click.secho(f"Config file not found: {config_path}. You may need to create it.", fg="yellow")
        ctx.obj = None
    else:
        ctx.obj = load_config(config_path)

@cli.command()
@click.pass_context
@click.option('--force', is_flag=True, help="Regenerate existing pages")
def generate(ctx, force: bool):
    """Read content_new/, generate pages using ADK multi-agent workflow"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    pipeline = WikiPipeline(ctx.obj)
    asyncio.run(pipeline.generate_pages(force=force))

@cli.command()
@click.pass_context
def index(ctx):
    """Rebuild the index.md based on generated wiki pages"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    pipeline = WikiPipeline(ctx.obj)
    asyncio.run(pipeline.build_index())

@cli.command()
@click.pass_context
def topics(ctx):
    """Extract and normalize topics across the wiki"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    from src.core.taxonomy import TaxonomyBuilder
    taxonomy_builder = TaxonomyBuilder(ctx.obj)
    asyncio.run(taxonomy_builder.build_taxonomy())

@cli.command()
@click.pass_context
def groups(ctx):
    """Generate organizational grouping pages based on metadata"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    from src.core.groupings import GroupingBuilder
    group_builder = GroupingBuilder(ctx.obj)
    asyncio.run(group_builder.build_groups())

@cli.command()
@click.pass_context
def consolidate(ctx):
    """Semantically merge duplicate content"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    from src.core.consolidator import Consolidator
    consolidator = Consolidator(ctx.obj)
    asyncio.run(consolidator.run_consolidation())

@cli.command()
@click.pass_context
def lint(ctx):
    """Run markdown-hero linting over the wiki"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    from src.core.lint_repair import LinterAndRepairer
    lr = LinterAndRepairer(ctx.obj)
    lr.run_lint()

@cli.command()
@click.pass_context
def repair(ctx):
    """Run linting and trigger the automatic ADK repair workflow"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    from src.core.lint_repair import LinterAndRepairer
    lr = LinterAndRepairer(ctx.obj)
    issues = lr.run_lint()
    asyncio.run(lr.run_repair(issues))

@cli.command()
@click.pass_context
def chat(ctx):
    """Start the BM25 RAG Chat Interface via NiceGUI"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    from src.ui.chat import WikiChatApp
    chat_app = WikiChatApp(ctx.obj)
    chat_app.run()

@cli.command()
@click.pass_context
@click.option('--output', default="wiki_export.docx", help="Output docx filename")
def export(ctx, output: str):
    """Export the wiki to a Word document"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    from src.core.exporter import Exporter
    exporter = Exporter(ctx.obj)
    exporter.export_word(output)

@cli.command()
@click.pass_context
def setup(ctx):
    """Interactive wizard to generate config and .env files (Stub)"""
    click.echo("Setup wizard is not fully implemented in this port yet.")
    click.echo("Please edit config/wiki_config.py manually.")

@cli.command()
@click.pass_context
def run_all(ctx):
    """Run all pipeline stages: generate -> index (More stages to come)"""
    if not ctx.obj:
        click.secho("Aborting: Valid configuration required.", fg="red")
        return
        
    pipeline = WikiPipeline(ctx.obj)
    asyncio.run(pipeline.generate_pages(force=False))
    asyncio.run(pipeline.build_index())

if __name__ == '__main__':
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ and "VERTEX_PROJECT" not in os.environ:
        click.secho("Warning: Make sure you are authenticated with Vertex AI (e.g. gcloud auth application-default login) and VERTEX_PROJECT is set.", fg="yellow")
        
    cli()
