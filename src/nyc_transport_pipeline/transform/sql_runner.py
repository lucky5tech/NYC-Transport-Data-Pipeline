from pathlib import Path

from nyc_transport_pipeline.database import get_engine
from nyc_transport_pipeline.logger import setup_logger


logger = setup_logger("transform")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SQL_DIRECTORY = PROJECT_ROOT / "sql"


def execute_sql_file(file_path: Path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    sql = file_path.read_text(encoding="utf-8").strip()

    if not sql:
        logger.warning("SQL file is empty: %s", file_path)
        return

    engine = get_engine()

    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(sql)

        logger.info("Successfully executed SQL: %s", file_path.name)

    except Exception:
        logger.exception("Failed to execute SQL: %s", file_path.name)
        raise

    finally:
        engine.dispose()


def run_staging_transformations() -> None:
    logger.info("Starting RAW to STAGING transformations")

    execute_sql_file(
        SQL_DIRECTORY / "staging" / "load_hourly_ridership.sql"
    )

    logger.info("RAW to STAGING transformations completed")


def run_analytics_transformations() -> None:
    logger.info("Starting STAGING to ANALYTICS transformations")

    execute_sql_file(
        SQL_DIRECTORY / "analytics" / "load_hourly_facts.sql"
    )

    logger.info("STAGING to ANALYTICS transformations completed")