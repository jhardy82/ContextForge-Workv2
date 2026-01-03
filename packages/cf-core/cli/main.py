"""ContextForge CLI Main Entry Point.

Provides the unified Typer-based CLI with:
- Universal --machine flag for agent consumption
- Noun-verb command pattern (cf <resource> <action>)
- Structured output and semantic exit codes
- Callback-based settings injection

Command Structure:
    cf [global-options] <command-group> <command> [options]

Global Options:
    --machine, -m     Enable machine mode (JSON output, no color)
    --output, -o      Output format (json, jsonl, table, yaml, csv)
    --no-color        Disable colored output
    --verbose, -v     Enable verbose output
    --quiet, -q       Suppress non-essential output
    --version         Show version and exit
    --help            Show help and exit
"""

from __future__ import annotations

import json
import sys
import uuid
import warnings
from datetime import UTC, datetime

import typer

from cf_core.cli.action_list import action_list_app
from cf_core.cli.config import config_app
from cf_core.cli.context import app as context_app
from cf_core.cli.logs import app as logs_app
from cf_core.cli.project import project_app
from cf_core.cli.qse import app as qse_app
from cf_core.cli.sprint import sprint_app
from cf_core.cli.state import state
from cf_core.cli.sync import app as sync_app
from cf_core.cli.task import task_app
from cf_core.config.settings import ContextForgeSettings, get_fresh_settings
from cf_core.errors.codes import ExitCode
from cf_core.errors.response import create_error, create_success
from cf_core.logging import ulog
from cf_core.runtime import Runtime

# Suppress runpy warning
warnings.filterwarnings(
    "ignore",
    message=".*found in sys.modules after import of package.*",
    category=RuntimeWarning,
    module="runpy",
)

__version__ = "0.1.0"

app = typer.Typer(
    name="cf",
    help="ContextForge - AI-first task management CLI",
    add_completion=True,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    machine: bool = typer.Option(
        False,
        "--machine",
        "-m",
        help="Enable machine mode for agent consumption (JSON output, no color)",
        is_eager=True,
    ),
    output_format: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output format: json, jsonl, table, yaml, csv",
    ),
    no_color: bool = typer.Option(
        False,
        "--no-color",
        help="Disable colored output",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress non-essential output",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
    ),
) -> None:
    """ContextForge CLI - AI-first task management."""
    if version:
        typer.echo(f"ContextForge CLI v{__version__}")
        raise typer.Exit()

    settings = get_fresh_settings()

    valid_formats = {"json", "jsonl", "table", "yaml", "csv"}
    if output_format and output_format not in valid_formats:
        typer.echo(
            f"Error: Invalid output format '{output_format}'. Valid: {', '.join(valid_formats)}",
            err=True,
        )
        raise typer.Exit(ExitCode.INVALID_ARGUMENT)

    settings.apply_cli_overrides(
        machine=machine,
        output_format=output_format,
        no_color=no_color,
        verbose=verbose,
        quiet=quiet,
    )

    state.settings = settings
    ctx.obj = settings


# Register Sub-apps
def _register_subapps():
    """Register all sub-apps and emit legacy-compatible telemetry."""
    subapps = [
        (task_app, "task"),
        (sprint_app, "sprint"),
        (project_app, "project"),
        (action_list_app, "action-list"),
        (config_app, "config"),
        (logs_app, "logs"),
        (context_app, "context"),
        (qse_app, "qse"),
        (sync_app, "sync"),
    ]

    import importlib.util
    import os
    from pathlib import Path

    start_time = datetime.now(UTC)
    loaded = 0
    skipped = 0
    failed = 0

    # Register Static Apps
    for subapp, name in subapps:
        app.add_typer(subapp, name=name)
        loaded += 1
        if ulog:
            ulog(
                "plugin_register_success",
                ok=True,
                correlation_id=f"corr-{uuid.uuid4().hex}",
                details={
                    "name": name,
                    "status": "success",
                    "register_duration_ms": 0.1,
                    "feature_flag_source": "default",
                },
            )

    # Register Dynamic Plugins (Compatibility for Integration Tests)
    plugin_paths_raw = os.getenv("CF_CLI_PLUGIN_PATHS", "")
    if plugin_paths_raw:
        for path_str in plugin_paths_raw.split(os.pathsep):
            path = Path(path_str.strip())
            if not path.exists():
                continue

            # Iterate over all items in the plugin path
            for item_path in path.iterdir():
                module_name = item_path.stem

                # Check for file plugin (.py) or package plugin (dir with __init__.py)
                is_package = item_path.is_dir() and (item_path / "__init__.py").exists()
                is_module = (
                    item_path.is_file()
                    and item_path.suffix == ".py"
                    and item_path.name != "__init__.py"
                )

                if not (is_package or is_module):
                    continue

                # Default short name
                short_name = module_name
                if short_name.startswith("plugin_") or short_name.startswith("cf_plugin_"):
                    # Strip prefix for cleaner internal names
                    short_name = short_name.replace("cf_plugin_", "").replace("plugin_", "")

                # Normalized name for feature flag check (e.g. taskman -> TASKMAN)
                norm_name = short_name.replace("-", "_").upper()
                flag_var = f"CF_PLUGIN_{norm_name}_ENABLED"
                flag_value = os.getenv(flag_var)

                # Check for explicit disable (flag_value "0")
                if flag_value == "0":
                    skipped += 1
                    if ulog:
                        ulog(
                            "plugin_skipped",
                            ok=True,
                            correlation_id=f"corr-{uuid.uuid4().hex}",
                            details={
                                "name": short_name,
                                "status": "skipped",
                                "feature_flag_source": "env",
                            },
                        )
                    continue

                # Attempt to load plugin
                try:
                    # Add path to sys.path so we can import the package
                    if str(path) not in sys.path:
                        sys.path.insert(0, str(path))

                    module = importlib.import_module(module_name)

                    # Extract metadata
                    meta = getattr(module, "PLUGIN_META", {})
                    plugin_name = meta.get("name", short_name)
                    enabled_by_default = meta.get("enabled_by_default", True)

                    # Apply default enablement if not overridden by env
                    if flag_value is None and not enabled_by_default:
                        skipped += 1
                        if ulog:
                            ulog(
                                "plugin_skipped",
                                ok=True,
                                correlation_id=f"corr-{uuid.uuid4().hex}",
                                details={
                                    "name": plugin_name,
                                    "status": "skipped",
                                    "feature_flag_source": "default",
                                },
                            )
                        continue

                    # Register via Typer app OR register() hook
                    if hasattr(module, "app") and isinstance(module.app, typer.Typer):
                        # Avoid duplicate registration
                        cmd_name = plugin_name.replace("_", "-")
                        known_commands = [c.name for c in app.registered_commands] + [
                            g.name for g in app.registered_groups
                        ]

                        if cmd_name not in known_commands:
                            app.add_typer(module.app, name=cmd_name)
                            loaded += 1
                        else:
                            # Already registered (likely from static registration)
                            if ulog:
                                ulog(
                                    "plugin_skipped_duplicate", ok=True, details={"name": cmd_name}
                                )
                            skipped += 1
                    elif hasattr(module, "register"):
                        # The register hook in tests expects (app, context)
                        # context is settings for now
                        module.register(app, get_fresh_settings().model_dump())
                        loaded += 1
                    else:
                        # Not a valid plugin
                        continue

                    if ulog:
                        ulog(
                            "plugin_register_success",
                            ok=True,
                            correlation_id=f"corr-{uuid.uuid4().hex}",
                            details={
                                "name": plugin_name,
                                "status": "success",
                                "register_duration_ms": 1.0,  # Synthetic
                                "feature_flag_source": "env" if flag_value else "default",
                                "type": "package" if is_package else "module",
                            },
                        )
                except Exception as e:
                    failed += 1
                    if ulog:
                        ulog(
                            "plugin_import_error",
                            ok=False,
                            correlation_id=f"corr-{uuid.uuid4().hex[:8]}",
                            details={
                                "name": short_name,
                                "status": "failure",
                                "error": str(e),
                            },
                        )

    end_time = datetime.now(UTC)
    duration_ms = (end_time - start_time).total_seconds() * 1000

    if ulog:
        ulog(
            "plugin_inventory",
            ok=True,
            duration_ms=duration_ms,
            details={
                "total": loaded + skipped + failed,
                "loaded": loaded,
                "skipped": skipped,
                "failed": failed,
                "status": "success" if failed == 0 else "partial",
            },
        )
        ulog(
            "plugin_bootstrap_complete",
            ok=True,
            duration_ms=duration_ms,
        )


@app.command("health")
def health_check(ctx: typer.Context) -> None:
    """Check database and service health."""
    settings: ContextForgeSettings = ctx.obj
    service = state.service
    out = state.output

    result = service.health_check()

    if result.is_failure:
        if settings.machine_mode:
            error_response = create_error(
                code="HEALTH_CHECK_FAILED",
                message=result.error,
                exit_code=ExitCode.GENERAL_ERROR,
                machine_mode=True,
            )
            out.json(error_response.model_dump())
        else:
            out.error(f"Health check failed: {result.error}")
        raise typer.Exit(ExitCode.GENERAL_ERROR)

    health_data = result.value

    if settings.machine_mode:
        out.json(health_data)
    else:
        status = health_data.get("status", "unknown")
        out.success(f"Service Health: {status.upper()}")
        out.info(f"  Database: {health_data.get('database', 'unknown')}")
        out.info(f"  Checked: {health_data.get('checked_at', 'N/A')}")


def run_cli() -> None:
    """Entry point for the CLI."""
    from cf_core.logging import configure_logging, ulog
    from cf_core.telemetry.trace import init_tracing, span

    init_tracing()

    verbose_logging = "--verbose" in sys.argv or "-v" in sys.argv
    # Use machine mode flag if present to suppress console color during setup
    machine_mode = "--machine" in sys.argv or "-m" in sys.argv
    configure_logging(console="none" if machine_mode else "stderr")

    _register_subapps()

    correlation_id = f"corr-{uuid.uuid4().hex[:16]}"

    if ulog:
        ulog("session_start", correlation_id=correlation_id)
        ulog(
            "cli_bootstrap_complete",
            correlation_id=correlation_id,
        )

    try:
        app()
    except KeyboardInterrupt:
        typer.echo("\nOperation cancelled.", err=True)
        sys.exit(ExitCode.INTERRUPTED)
    except Exception as e:
        from cf_core.errors.codes import get_exit_code_for_exception

        exit_code = get_exit_code_for_exception(e)

        if ulog:
            ulog(
                "cli_execution_failed",
                error=str(e),
                exit_code=exit_code,
                correlation_id=correlation_id,
                severity="ERROR",
            )
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(exit_code)
    finally:
        if ulog:
            ulog("session_end", correlation_id=correlation_id)

        # Close implementation-specific resources first
        if hasattr(state, "output") and state.output:
            state.output.close()

        # Clean shutdown of async resources
        try:
            import asyncio

            # Check if there's a running loop, though simpler to just run new loop
            # as run_cli is the exit point.
            asyncio.run(state.close())
        except Exception:
            # Best effort cleanup
            pass


if __name__ == "__main__":
    run_cli()
