from logging.config import fileConfig
import os
from dotenv import load_dotenv
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from backend.database.db import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- Load environment variables reliably ---
# Get the directory containing alembic.ini
ini_path_str = config.config_file_name
if ini_path_str is None:
    raise ValueError("Could not determine path to alembic.ini from config")
ini_path = Path(ini_path_str).resolve() # Ensure we have an absolute path
# Go 4 levels up from alembic.ini dir to reach project root
project_root = ini_path.parent.parent.parent.parent 
dotenv_path = project_root / '.env'

# Load .env using python-dotenv
load_success = load_dotenv(
    dotenv_path=dotenv_path, 
    override=True,          # Overwrite existing vars if necessary
    encoding='utf-8-sig',   # Handle potential BOM
)

# Get database credentials from environment
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Construct the database URL
db_url = None
if all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT]):
    db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    config.set_main_option("sqlalchemy.url", db_url)
else:
    print("ERROR: One or more database environment variables are missing! Using fallback or default URL if defined in alembic.ini might be necessary.")

# --- Standard Alembic setup ---

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    if not url:
         raise ValueError("Database URL not configured for offline mode.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Ensure the URL was set
    if not config.get_main_option("sqlalchemy.url"):
        print("ERROR: sqlalchemy.url not set in config for online mode!")
        return # Or raise error
        
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
