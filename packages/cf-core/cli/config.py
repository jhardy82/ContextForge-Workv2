"""Configuration CLI Commands."""

from __future__ import annotations

import typing

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None

try:
    import tomli_w
except ImportError:
    tomli_w = None

from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from cf_core.config.settings import get_fresh_settings

console = Console()

# Define the app variable expected by main.py
config_app = typer.Typer(
    help="Manage ContextForge configuration and profiles.",
    no_args_is_help=True,
)

# Path to user config file (from settings convention)
USER_CONFIG_PATH = Path.home() / ".contextforge" / "config.toml"


@config_app.command(name="show")
def show_config(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON."),
    hide_secrets: bool = typer.Option(
        True, "--hide-secrets/--show-secrets", help="Redact secret values."
    ),
):
    """Show the current effective configuration (merged from all sources)."""
    settings = get_fresh_settings()
    data = settings.model_dump(mode="json")

    # Redact secrets
    if hide_secrets:
        if "database" in data and isinstance(data["database"], dict):
            if "password" in data["database"]:
                data["database"]["password"] = "*****"
            if "url" in data["database"] and data["database"]["url"]:
                # Basic redaction for connection strings
                url = str(data["database"]["url"])
                if ":" in url and "@" in url:
                    try:
                        # naive replacement
                        prefix = url.split("://")[0]
                        rest = url.split("://")[1]
                        creds, host = rest.split("@", 1)
                        if ":" in creds:
                            user, _ = creds.split(":", 1)
                            data["database"]["url"] = f"{prefix}://{user}:*****@{host}"
                    except Exception:
                        pass

    if json_output:
        import json

        console.print_json(json.dumps(data))
    else:
        console.print("[bold blue]Current Configuration (Merged):[/bold blue]")
        # Prefer TOML for readability, fallback to JSON
        if tomli_w:
            try:
                toml_str = tomli_w.dumps(data)
                syntax = Syntax(toml_str, "toml", theme="monokai", line_numbers=False)
                console.print(syntax)
                return
            except Exception:
                pass

        # Fallback to JSON print
        import json

        console.print_json(json.dumps(data))


@config_app.command(name="list")
def list_config(
    filter_key: str = typer.Argument(None, help="Filter by key prefix (e.g., 'logging')"),
):
    """List configuration values in a flat table format."""
    settings = get_fresh_settings()
    data = settings.model_dump(mode="json")

    table = Table(title="Configuration Values")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")

    def flatten(d: dict[str, Any], parent_key: str = "") -> dict[str, Any]:
        items: dict[str, Any] = {}
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(flatten(v, new_key))
            else:
                items[new_key] = v
        return items

    flat_data = flatten(data)

    for key, value in sorted(flat_data.items()):
        if filter_key and filter_key not in key:
            continue
        # Naive redaction
        if any(secret in key.lower() for secret in ["password", "secret", "token", "key"]):
            value = "*****"
        table.add_row(key, str(value))

    console.print(table)


@config_app.command(name="set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key (e.g. logging.level)"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set a configuration value in the user's config.toml file."""
    if not tomllib or not tomli_w:
        console.print(
            "[red]Error:[/red] 'tomli' and 'tomli-w' libraries are required for editing config files."
        )
        console.print("Please install them via pip or poetry.")
        raise typer.Exit(1)

    if not USER_CONFIG_PATH.exists():
        USER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        USER_CONFIG_PATH.touch()

    # Read existing config
    try:
        with open(USER_CONFIG_PATH, "rb") as f:
            config_data = tomllib.load(f)
    except Exception as e:
        console.print(
            f"[yellow]Warning:[/yellow] Could not read existing config ({e}). Starting fresh."
        )
        config_data = {}

    # Update value (handle nested keys like logging.level)
    keys = key.split(".")
    current = config_data
    for i, k in enumerate(keys[:-1]):
        if k not in current:
            current[k] = {}

        # Check if we are trying to index into a non-dict
        if not isinstance(current[k], dict):
            console.print(
                f"[red]Error:[/red] Key collision at '{k}' - existing value is '{current[k]}' (not a table)."
            )
            raise typer.Exit(1)

        current = current[k]

    # Simple type inference
    final_key = keys[-1]
    cleaned_value: Any = value
    if value.lower() == "true":
        cleaned_value = True
    elif value.lower() == "false":
        cleaned_value = False
    elif value.isdigit():
        cleaned_value = int(value)

    current[final_key] = cleaned_value

    # Write back
    try:
        with open(USER_CONFIG_PATH, "wb") as f:
            tomli_w.dump(config_data, f)
        console.print(
            f"[green]Success:[/green] Set '{key}' to '{cleaned_value}' in {USER_CONFIG_PATH}"
        )
    except Exception as e:
        console.print(f"[red]Error writing config:[/red] {e}")
        raise typer.Exit(1)


@config_app.command(name="file")
def get_config_file():
    """Print the path of the user configuration file."""
    console.print(str(USER_CONFIG_PATH))
