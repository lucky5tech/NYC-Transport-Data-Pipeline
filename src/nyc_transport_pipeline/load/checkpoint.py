
from sqlalchemy import text

from nyc_transport_pipeline.database import get_engine
from nyc_transport_pipeline.logger import setup_logger


logger = setup_logger("checkpoint")


def get_checkpoint(pipeline_name: str) -> int:
    engine = get_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT next_offset
                    FROM metadata.pipeline_checkpoints
                    WHERE pipeline_name = :pipeline_name
                """),
                {"pipeline_name": pipeline_name},
            )

            row = result.fetchone()

            if row is None:
                return 0

            return row.next_offset

    finally:
        engine.dispose()


def update_checkpoint(
    connection,
    pipeline_name: str,
    next_offset: int,
    status: str = "running",
) -> None:

    connection.execute(
        text("""
            INSERT INTO metadata.pipeline_checkpoints (
                pipeline_name,
                next_offset,
                status,
                updated_at
            )
            VALUES (
                :pipeline_name,
                :next_offset,
                :status,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT (pipeline_name)
            DO UPDATE SET
                next_offset = EXCLUDED.next_offset,
                status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
        """),
        {
            "pipeline_name": pipeline_name,
            "next_offset": next_offset,
            "status": status,
        },
    )

    logger.info(
        "Checkpoint updated: %s | next_offset=%s | status=%s",
        pipeline_name,
        next_offset,
        status,
    )


def set_checkpoint_status(
    pipeline_name: str,
    status: str,
) -> None:
    engine = get_engine()

    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO metadata.pipeline_checkpoints (
                        pipeline_name,
                        next_offset,
                        status,
                        updated_at
                    )
                    VALUES (
                        :pipeline_name,
                        0,
                        :status,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (pipeline_name)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        updated_at = CURRENT_TIMESTAMP
                """),
                {
                    "pipeline_name": pipeline_name,
                    "status": status,
                },
            )

        logger.info(
            "Checkpoint status updated: %s | status=%s",
            pipeline_name,
            status,
        )

    finally:
        engine.dispose()
