
from nyc_transport_pipeline.extract.subway import fetch_subway_data
from nyc_transport_pipeline.extract.bus import fetch_bus_data

from nyc_transport_pipeline.load.postgres_loader import (
    load_subway_batch,
    load_bus_batch,
)

from nyc_transport_pipeline.load.checkpoint import (
    get_checkpoint,
    set_checkpoint_status,
)

from nyc_transport_pipeline.logger import setup_logger


logger = setup_logger("pipeline")


def run_pipeline(
    batch_size: int = 1000,
    max_records: int | None = None,
) -> None:

    logger.info("Starting NYC Transport Pipeline")

    total_subway_records = 0
    total_bus_records = 0

    try:
        # SUBWAY

        logger.info("Starting subway extraction and loading")

        subway_offset = get_checkpoint("subway")
        subway_processed = 0

        logger.info(
            "Resuming subway from offset=%s",
            subway_offset,
        )

        set_checkpoint_status("subway", "running")

        try:
            for batch in fetch_subway_data(
                batch_size=batch_size,
                max_records=max_records,
                start_offset=subway_offset,
            ):
                next_offset = subway_offset + len(batch)

                loaded = load_subway_batch(
                    batch,
                    next_offset=next_offset,
                )

                subway_offset = next_offset
                subway_processed += len(batch)
                total_subway_records += loaded

                logger.info(
                    "Subway progress: inserted=%s | next_offset=%s",
                    total_subway_records,
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

        # BUS

        logger.info("Starting bus extraction and loading")

        bus_offset = get_checkpoint("bus")
        bus_processed = 0

        logger.info(
            "Resuming bus from offset=%s",
            bus_offset,
        )

        set_checkpoint_status("bus", "running")

        try:
            for batch in fetch_bus_data(
                batch_size=batch_size,
                max_records=max_records,
                start_offset=bus_offset,
            ):
                next_offset = bus_offset + len(batch)

                loaded = load_bus_batch(
                    batch,
                    next_offset=next_offset,
                )

                bus_offset = next_offset
                bus_processed += len(batch)
                total_bus_records += loaded

                logger.info(
                    "Bus progress: inserted=%s | next_offset=%s",
                    total_bus_records,
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

        logger.info(
            "Pipeline completed. Subway inserted: %s, Bus inserted: %s",
            total_subway_records,
            total_bus_records,
        )

    except Exception:
        logger.exception("Pipeline failed")
        raise


if __name__ == "__main__":
    run_pipeline()

