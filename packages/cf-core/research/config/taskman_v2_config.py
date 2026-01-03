"""
TaskMan-v2 Research Configuration

Configures research swarm to analyze TaskMan-v2 codebase and PostgreSQL databases
instead of legacy SQLite and root-level CLI files.
"""

from pathlib import Path

# TaskMan-v2 base directory
TASKMAN_V2_ROOT = Path("TaskMan-v2")

# PostgreSQL Database Configuration
TASKMAN_V2_CONFIG = {
    # Database Configuration
    "db_type": "postgresql",
    "db_host": "172.25.14.122",
    "db_port": 5432,
    "db_name": "taskman_v2",
    "db_user": "contextforge",
    "db_password": "contextforge",
    "db_path": None,  # PostgreSQL doesn't use file paths

    # Secondary Database (ContextForge)
    "db_contextforge": {
        "type": "postgresql",
        "host": "172.25.14.122",
        "port": 5432,
        "database": "ContextForge",
        "user": "contextforge",
        "password": "contextforge"
    },

    # TaskMan-v2 Directory Paths
    "taskman_root": str(TASKMAN_V2_ROOT),
    "cli_root": str(TASKMAN_V2_ROOT / "cli"),
    "backend_root": str(TASKMAN_V2_ROOT / "backend-api"),
    "backend_services": str(TASKMAN_V2_ROOT / "backend"),
    "mcp_server_py": str(TASKMAN_V2_ROOT / "mcp-server"),
    "mcp_server_ts": str(TASKMAN_V2_ROOT / "mcp-server-ts"),
    "shared_root": str(TASKMAN_V2_ROOT / "shared"),
    "frontend_root": str(TASKMAN_V2_ROOT / "src"),

    # Output Directories (TaskMan-v2 specific)
    "evidence_dir": str(TASKMAN_V2_ROOT / "evidence"),
    "research_reports_dir": str(TASKMAN_V2_ROOT / "research"),
    "specs_output_dir": str(TASKMAN_V2_ROOT / "specs"),
    "knowledge_graph_output": str(TASKMAN_V2_ROOT / "knowledge_graph"),

    # Validation Configuration
    "validation_reports": "validation_reports",  # Use root-level validation reports for now
    "validation_report_path": "validation_reports/flow_FLOW-20251117-175714-501f5ec7.json",

    # Output System Files (TaskMan-v2)
    "output_files": [
        str(TASKMAN_V2_ROOT / "backend-api" / "**" / "*.py"),
        str(TASKMAN_V2_ROOT / "shared" / "**" / "*.py"),
    ],

    # CLI Files to Analyze (TaskMan-v2)
    "cli_files": [
        "cf_cli.py",          # Root-level CF CLI
        "tasks_cli.py",       # Root-level tasks CLI
        "projects_cli.py",    # Root-level projects CLI
        "sprints_cli.py",     # Root-level sprints CLI
        "dbcli.py",           # Root-level DB CLI
        # TaskMan-v2 CLI files (when they exist)
        str(TASKMAN_V2_ROOT / "cli" / "**" / "*.py"),
    ],

    # Analysis Scope
    "analyze_typescript": False,  # Set to True to include TypeScript MCP server
    "analyze_frontend": False,    # Set to True to include React frontend
    "focus_areas": [
        "backend-api",  # Priority 1
        "cli",          # Priority 2
        "mcp-server",   # Priority 3
        "database",     # Priority 4
    ]
}


def get_default_config():
    """
    Get default research configuration

    Returns configuration for TaskMan-v2 analysis by default.
    For legacy system analysis, create a separate config.
    """
    return TASKMAN_V2_CONFIG.copy()


def get_postgres_connection_string(config=None):
    """
    Generate PostgreSQL connection string from config

    Args:
        config: Configuration dictionary (defaults to TASKMAN_V2_CONFIG)

    Returns:
        PostgreSQL connection string
    """
    if config is None:
        config = TASKMAN_V2_CONFIG

    return (
        f"postgresql://{config['db_user']}:{config['db_password']}"
        f"@{config['db_host']}:{config['db_port']}/{config['db_name']}"
    )


def get_contextforge_connection_string(config=None):
    """
    Generate ContextForge PostgreSQL connection string

    Args:
        config: Configuration dictionary (defaults to TASKMAN_V2_CONFIG)

    Returns:
        PostgreSQL connection string
    """
    if config is None:
        config = TASKMAN_V2_CONFIG

    cf = config['db_contextforge']
    return (
        f"postgresql://{cf['user']}:{cf['password']}"
        f"@{cf['host']}:{cf['port']}/{cf['database']}"
    )
