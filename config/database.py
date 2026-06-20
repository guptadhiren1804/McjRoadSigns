"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Database Connection Management (Secure Pattern)
"""

import os
import logging
from contextlib import contextmanager
from psycopg_pool import ConnectionPool

logger = logging.getLogger("McjRoadSigns.Database")
logging.basicConfig(level=logging.INFO)

# 1. Fetch values strictly. If critical configs are missing, fail immediately.
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")  # Safe to default to local network loopback
DB_PORT = os.getenv("DB_PORT", "5432")       # Safe to default to standard Postgres port

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Strict enforcement check
if not all([DB_NAME, DB_USER, DB_PASSWORD]):
    logger.critical("CRITICAL CONFIGURATION ERROR: DB_NAME, DB_USER, or DB_PASSWORD is not set in the environment variables!")
    raise EnvironmentError("Missing critical database credentials. Please check your active .env file.")

# 2. Build Connection String
CONNECTION_STRING = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

# 3. Initialize Pool
db_pool = None
try:
    db_pool = ConnectionPool(
        conninfo=CONNECTION_STRING,
        min_size=2,
        max_size=10,
        open=True
    )
    logger.info("Successfully initialized secure PostgreSQL connection pool.")
except Exception as e:
    logger.critical(f"Failed to initialize database pool: {e}")
    raise e

@contextmanager
def get_db_cursor():
    """Leases and safely handles an active database connection."""
    if db_pool is None:
        raise RuntimeError("Database connection pool is not initialized.")
        
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            try:
                yield cursor
                conn.commit()
            except Exception as error:
                conn.rollback()
                logger.error(f"Database transaction error rolled back: {error}")
                raise error
