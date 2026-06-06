import os
import logging
from app import app, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_models_to_postgres():
    """Create PostgreSQL tables from SQLAlchemy models."""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error('DATABASE_URL environment variable not set')
        raise RuntimeError('DATABASE_URL environment variable must be set for PostgreSQL.')

    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    with app.app_context():
        logger.info('Creating PostgreSQL tables from SQLAlchemy models...')
        db.create_all()
        logger.info('PostgreSQL tables created successfully from models.')


if __name__ == '__main__':
    migrate_models_to_postgres()
