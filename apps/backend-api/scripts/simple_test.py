
def log(msg):
    with open("simple_test.log", "a") as f:
        f.write(str(msg) + "\n")

log("Starting V2")
try:
    log("Alembic imported")
    from alembic.config import Config
    from alembic.script import ScriptDirectory
    log("Imports done")

    cfg = Config("alembic.ini")
    location = cfg.get_main_option("script_location")
    log(f"Config loaded. Script location: {location}")

    script = ScriptDirectory.from_config(cfg)
    log(f"Script directory loaded: {script.dir}")

    from alembic import command
    command.upgrade(cfg, "head")
    log("Command executed")

except SystemExit as e:
    log(f"SystemExit caught: {e}")
except Exception as e:
    log(f"Error: {e}")
    import traceback
    log(traceback.format_exc())
