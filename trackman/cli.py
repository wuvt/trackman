import click
import os
import random
import string
from flask import json
from . import app, db_utils, lib, redis_conn


@app.cli.command()
def init_embedded_db():
    """Initialize and seed the embedded database with sample data."""

    # The SQLALCHEMY_DATABASE_URI config option will match the corresponding
    # environment variable when we are using the embedded database.
    if app.config['SQLALCHEMY_DATABASE_URI'] != \
            os.getenv('SQLALCHEMY_DATABASE_URI'):
        return

    click.echo("Initialize the database...")

    # Generate a random password for the admin user
    password = ''.join(random.SystemRandom().sample(
        string.ascii_letters + string.digits, 12))
    click.echo('Password for admin will be set to: {0}'.format(password))

    db_utils.initdb('admin', password)

    click.echo("Database initialized.")

    click.echo("Add sample data...")
    db_utils.add_sample_data()
    click.echo("Sample data added.")


@app.cli.command()
@click.option('--username', default="admin")
@click.password_option()
def initdb(username, password):
    """Initialize the database."""
    click.echo("Initialize the database...")
    db_utils.initdb(username, password)
    click.echo("Database initialized.")


@app.cli.command()
def sampledata():
    """Add some sample data to the database."""
    click.echo("Add sample data...")
    db_utils.add_sample_data()
    click.echo("Sample data added.")


@app.cli.command()
@click.option('--ignore-case/--no-ignore-case', default=False,
              help="Ignore capitalization.")
def deduplicate_all_tracks(ignore_case):
    """Merge identical tracks."""
    lib.deduplicate_all_tracks(ignore_case)


@app.cli.command()
def autofill_na_labels():
    """Try to find an appropriate label for tracks without one."""
    lib.autofill_na_labels()


@app.cli.command()
def email_weekly_charts():
    """If configured, email the weekly charts."""
    lib.email_weekly_charts()


@app.cli.command()
def prune_empty_djsets():
    """Prune empty DJSets from the database."""
    lib.prune_empty_djsets()


@app.cli.command()
def cleanup_dj_list():
    """Find DJs with no recent sets and hide them from main list."""
    lib.cleanup_dj_list()


@app.cli.command()
@click.option('--message', prompt=True)
def send_message(message):
    """Send a message to the current DJ."""
    r = redis_conn.publish('trackman_dj_live', json.dumps({
        'event': "message",
        'data': message,
    }))
    click.echo("Message delivered to {0} clients".format(r))
