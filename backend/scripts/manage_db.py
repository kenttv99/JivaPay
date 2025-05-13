import click

from backend.database.engine import engine
from backend.database.db import Base

# Import existing seed functions
from backend.scripts.seed_config import seed_config as seed_config_main
from backend.scripts.seed_data import seed_data as seed_data_main

@click.group()
def cli():
    """Management commands for database initialization and seeding."""
    pass

@cli.command()
def init():
    """Initialize the database by creating all tables."""
    click.echo("Initializing database...")
    Base.metadata.create_all(bind=engine)
    click.echo("Database initialization complete.")

@cli.command()
def seed_config():
    """Seed default configuration settings into the database."""
    click.echo("Seeding default configuration settings...")
    seed_config_main()
    click.echo("Configuration seeding complete.")

@cli.command()
def seed_data():
    """Seed initial roles and default admin user into the database."""
    click.echo("Seeding initial data (roles, admin user)...")
    seed_data_main()
    click.echo("Initial data seeding complete.")

if __name__ == "__main__":
    cli() 