import click
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from . import app, db_utils, lib, pubsub, tasks


@app.cli.command('init_embedded_db')
def init_embedded_db():
    """Initialize and seed the embedded database with sample data."""

    # The SQLALCHEMY_DATABASE_URI config option will match the corresponding
    # environment variable when we are using the embedded database.
    if app.config['SQLALCHEMY_DATABASE_URI'] != \
            os.getenv('SQLALCHEMY_DATABASE_URI'):
        return

    click.echo("Initialize the database...")
    db_utils.initdb()
    click.echo("Database initialized.")

    click.echo("Add sample data...")
    db_utils.add_sample_data()
    click.echo("Sample data added.")


@app.cli.command()
def initdb():
    """Initialize the database."""
    click.echo("Initialize the database...")
    db_utils.initdb()
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
    result = pubsub.publish(
        app.config['PUBSUB_PUB_URL_DJ'],
        message={
            'event': "message",
            'data': message,
        })
    click.echo("Message delivered to {0} clients".format(
        result['subscribers']))


@app.cli.command()
def run_scheduler():
    click.echo("Starting scheduler...")

    scheduler = BlockingScheduler()
    scheduler.add_job(tasks.email_weekly_charts, 'cron',
                      day_of_week=0, hour=0, minute=0, second=0)
    scheduler.add_job(tasks.deduplicate_tracks, 'cron',
                      hour=3, minute=0, second=0)
    scheduler.add_job(tasks.playlist_cleanup, 'cron',
                      hour=6, minute=0, second=0)
    scheduler.add_job(tasks.cleanup_dj_list_task, 'cron',
                      day_of_week=1, hour=0, minute=0, second=0)
    scheduler.add_job(tasks.internal_ping, 'interval', minutes=1)
    scheduler.add_job(tasks.cleanup_sessions_and_claim_tokens, 'cron',
                      hour=1, minute=0, second=0)
    scheduler.start()
