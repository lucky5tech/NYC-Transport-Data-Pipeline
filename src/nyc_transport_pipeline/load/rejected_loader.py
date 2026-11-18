from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

from nyc_transport_pipeline.logger import setup_logger


logger = setup_logger("rejected")


def load_rejected_batch(
    connection,
    pipeline_name: str,
    rejected_records: list[dict],
) -> int:

    if not rejected_records:
        return 0

    metadata = MetaData()

    rejected_table = Table(
        "rejected_records",
        metadata,
        schema="metadata",
        autoload_with=connection,
    )

    rows = [
        {
            "pipeline_name": pipeline_name,
            "source_offset": record["source_offset"],
            "source_data": record["source_data"],
            "validation_errors": record["validation_errors"],
        }
        for record in rejected_records
    ]

    stmt = insert(rejected_table).values(rows)

    stmt = stmt.on_conflict_do_nothing(
        constraint="uq_rejected_record"
    )

    result = connection.execute(stmt)

    inserted_count = result.rowcount

    logger.info(
        "Rejected records saved: %s | inserted=%s",
        pipeline_name,
        inserted_count,
    )

    return inserted_count