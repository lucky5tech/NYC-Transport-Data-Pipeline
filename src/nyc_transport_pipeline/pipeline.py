
from nyc_transport_pipeline.extract.subway import fetch_subway_data
from nyc_transport_pipeline.extract.bus import fetch_bus_data
from nyc_transport_pipeline.transform.sql_runner import (
    run_staging_transformations,
    run_analytics_transformations,
)
from nyc_transport_pipeline.load.postgres_loader import (
    load_subway_batch,
    load_bus_batch,
)

from nyc_transport_pipeline.load.checkpoint import (
    get_checkpoint,
    set_checkpoint_status,
)

from nyc_transport_pipeline.validation.validators import (
    validate_subway_record,
    validate_bus_record,
)

from nyc_transport_pipeline.logger import setup_logger


logger = setup_logger("pipeline")


def run_pipeline(
    batch_size: int = 1000,
    max_records: int | None = None,
) -> None:

    logger.info("Starting NYC Transport Pipeline")

    # Overall statistics
    total_subway_records = 0
    total_bus_records = 0

    total_subway_rejected = 0
    total_bus_rejected = 0

    total_subway_duplicates = 0
    total_bus_duplicates = 0

    # ==========================================
    # SUBWAY PIPELINE
    # ==========================================

    logger.info("Starting subway extraction and loading")

    subway_offset = get_checkpoint("subway")
    subway_processed = 0

    logger.info("Resuming subway from offset=%s", subway_offset)

    set_checkpoint_status("subway", "running")

    try:
        for batch in fetch_subway_data(
            batch_size=batch_size,
            max_records=max_records,
            start_offset=subway_offset,
        ):

            valid_records = []
            rejected_records = []

            # Data validation
            for index, record in enumerate(batch):

                errors = validate_subway_record(record)

                if errors:
                    rejected_records.append({
                        "source_offset": subway_offset + index,
                        "source_data": record,
                        "validation_errors": errors,
                    })
                else:
                    valid_records.append(record)

            next_offset = subway_offset + len(batch)

            # Load valid and rejected records
            loaded = load_subway_batch(
                records=valid_records,
                rejected_records=rejected_records,
                next_offset=next_offset,
            )

            # Calculate batch statistics
            duplicates = len(valid_records) - loaded

            total_subway_records += loaded
            total_subway_rejected += len(rejected_records)
            total_subway_duplicates += duplicates

            subway_processed += len(batch)
            subway_offset = next_offset

            logger.info(
                "Subway batch processed: "
                "received=%s | inserted=%s | rejected=%s | "
                "duplicates=%s | next_offset=%s",
                len(batch),
                loaded,
                len(rejected_records),
                duplicates,
                subway_offset,
            )

        subway_status = (
            "paused"
            if max_records is not None
            and subway_processed >= max_records
            else "completed"
        )

        set_checkpoint_status("subway", subway_status)

    except Exception:
        set_checkpoint_status("subway", "failed")
        raise


    logger.info("Starting bus extraction and loading")

    bus_offset = get_checkpoint("bus")
    bus_processed = 0

    logger.info("Resuming bus from offset=%s", bus_offset)

    set_checkpoint_status("bus", "running")

    try:
        for batch in fetch_bus_data(
            batch_size=batch_size,
            max_records=max_records,
            start_offset=bus_offset,
        ):

            valid_records = []
            rejected_records = []

            # Data validation
            for index, record in enumerate(batch):

                errors = validate_bus_record(record)

                if errors:
                    rejected_records.append({
                        "source_offset": bus_offset + index,
                        "source_data": record,
                        "validation_errors": errors,
                    })
                else:
                    valid_records.append(record)

            next_offset = bus_offset + len(batch)

            # Load valid and rejected records
            loaded = load_bus_batch(
                records=valid_records,
                rejected_records=rejected_records,
                next_offset=next_offset,
            )

            # Calculate batch statistics
            duplicates = len(valid_records) - loaded

            total_bus_records += loaded
            total_bus_rejected += len(rejected_records)
            total_bus_duplicates += duplicates

            bus_processed += len(batch)
            bus_offset = next_offset

            logger.info(
                "Bus batch processed: "
                "received=%s | inserted=%s | rejected=%s | "
                "duplicates=%s | next_offset=%s",
                len(batch),
                loaded,
                len(rejected_records),
                duplicates,
                bus_offset,
            )

        bus_status = (
            "paused"
            if max_records is not None
            and bus_processed >= max_records
            else "completed"
        )

        set_checkpoint_status("bus", bus_status)

    except Exception:
        set_checkpoint_status("bus", "failed")
        raise

        # Run transformations only after both sources are completed
    if subway_status == "completed" and bus_status == "completed":
        logger.info("Starting database transformations")

        run_staging_transformations()
        run_analytics_transformations()

        logger.info("All database transformations completed")
    else:
        logger.warning(
            "Skipping transformations: "
            "subway_status=%s, bus_status=%s",
            subway_status,
            bus_status,
        )


    logger.info(
        "Pipeline completed.\n"
        "Subway: received=%s | inserted=%s | "
        "rejected=%s | duplicates=%s\n"
        "Bus: received=%s | inserted=%s | "
        "rejected=%s | duplicates=%s",
        subway_processed,
        total_subway_records,
        total_subway_rejected,
        total_subway_duplicates,
        bus_processed,
        total_bus_records,
        total_bus_rejected,
        total_bus_duplicates,
    )


if __name__ == "__main__":
    run_pipeline()


