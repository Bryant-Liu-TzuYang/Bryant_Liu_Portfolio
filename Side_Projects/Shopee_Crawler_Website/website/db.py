import sqlite3
from datetime import datetime
import pytz

import click
from flask import current_app, g

# 設定 UTC+8 時區
taipei_tz = pytz.timezone('Asia/Taipei')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False  # Allow connections from different threads
        )
        g.db.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent access
        g.db.execute('PRAGMA journal_mode=WAL;')
        # Set busy timeout to handle concurrent access
        g.db.execute('PRAGMA busy_timeout=30000;')  # 30 seconds

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """cleaer the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


sqlite3.register_converter(
    """tells Python how to interpret timestamp values in the database. We convert the value to a datetime.datetime with GMT+8 timezone."""
    "timestamp", lambda v: datetime.fromisoformat(v.decode()).replace(tzinfo=taipei_tz)
)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
