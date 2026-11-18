from nyc_transport_pipeline.load.rejected_loader import load_rejected_batch
from datetime import datetime
from decimal import Decimal
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert
from nyc_transport_pipeline.database import get_engine
from nyc_transport_pipeline.logger import setup_logger
from nyc_transport_pipeline.load.checkpoint import update_checkpoint

logger = setup_logger("load")


def load_subway_batch(
    records: list[dict],
    rejected_records: list[dict] | None = None,
    next_offset: int | None = None,
) -> int:

    rejected_records = rejected_records or []

    if not records and not rejected_records:
        return 0

    engine = get_engine()

    try:
        metadata = MetaData()

        subway_table = Table(
            "subway_hourly_ridership",
            metadata,
            schema="raw",
            autoload_with=engine,
        )

        rows = []

        for record in records:
            row = {
                "transit_timestamp": datetime.fromisoformat(
                    record["transit_timestamp"]
                ),
                "transit_mode": record.get("transit_mode"),
                "station_complex_id": record.get("station_complex_id"),
                "station_complex": record.get("station_complex"),
                "borough": record.get("borough"),
                "payment_method": record.get("payment_method"),
                "fare_class_category": record.get("fare_class_category"),
                "ridership": (
                    int(Decimal(record["ridership"]))
                    if record.get("ridership") is not None
                    else None
                ),
                "transfers": (
                    int(Decimal(record["transfers"]))
                    if record.get("transfers") is not None
                    else None
                ),
                "latitude": (
                    Decimal(record["latitude"])
                    if record.get("latitude") is not None
                    else None
                ),
                "longitude": (
                    Decimal(record["longitude"])
                    if record.get("longitude") is not None
                    else None
                ),
                "source_data": record,
            }

            rows.append(row)

        with engine.begin() as connection:

            inserted_count = 0

            if rows:
                stmt = insert(subway_table).values(rows)

                stmt = stmt.on_conflict_do_nothing(
                    constraint="uq_subway_hourly_natural_key"
                )

                stmt = stmt.returning(subway_table.c.id)

                result = connection.execute(stmt)
                inserted_count = len(result.fetchall())

            rejected_count = load_rejected_batch(
                connection=connection,
                pipeline_name="subway",
                rejected_records=rejected_records,
            )

            if next_offset is not None:
                update_checkpoint(
                    connection=connection,
                    pipeline_name="subway",
                    next_offset=next_offset,
                )

        logger.info(
            "Subway batch processed: inserted=%s | rejected=%s | duplicates=%s",
            inserted_count,
            rejected_count,
            len(rows) - inserted_count,
        )

        return inserted_count

    except Exception:
        logger.exception("Failed to load subway batch")
        raise

    finally:
        engine.dispose()


def load_bus_batch(
    records: list[dict],
    rejected_records: list[dict] | None = None,
    next_offset: int | None = None,
) -> int:

    rejected_records = rejected_records or []

    if not records and not rejected_records:
        return 0

    engine = get_engine()

    try:
        metadata = MetaData()

        bus_table = Table(
            "bus_hourly_ridership",
            metadata,
            schema="raw",
            autoload_with=engine,
        )

        rows = []

        for record in records:
            row = {
                "transit_timestamp": datetime.fromisoformat(
                    record["transit_timestamp"]
                ),
                "bus_route": record.get("bus_route"),
                "payment_method": record.get("payment_method"),
                "fare_class_category": record.get("fare_class_category"),
                "ridership": (
                    int(Decimal(record["ridership"]))
                    if record.get("ridership") is not None
                    else None
                ),
                "transfers": (
                    int(Decimal(record["transfers"]))
                    if record.get("transfers") is not None
                    else None
                ),
                "source_data": record,
            }

            rows.append(row)

        with engine.begin() as connection:

            inserted_count = 0

            if rows:
                stmt = insert(bus_table).values(rows)

                stmt = stmt.on_conflict_do_nothing(
                    constraint="uq_bus_hourly_natural_key"
                )

                stmt = stmt.returning(bus_table.c.id)

                result = connection.execute(stmt)
                inserted_count = len(result.fetchall())

            rejected_count = load_rejected_batch(
                connection=connection,
                pipeline_name="bus",
                rejected_records=rejected_records,
            )

            if next_offset is not None:
                update_checkpoint(
                    connection=connection,
                    pipeline_name="bus",
                    next_offset=next_offset,
                )

        logger.info(
            "Bus batch processed: inserted=%s | rejected=%s | duplicates=%s",
            inserted_count,
            rejected_count,
            len(rows) - inserted_count,
        )

        return inserted_count

    except Exception:
        logger.exception("Failed to load bus batch")
        raise

    finally:
        engine.dispose()
