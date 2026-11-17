
from collections.abc import Iterator

from nyc_transport_pipeline.extract.api_client import fetch_data_in_batches


SUBWAY_ENDPOINT = "https://data.ny.gov/resource/5wq4-mkjj.json"


def fetch_subway_data(
    batch_size: int = 50000,
    max_records: int | None = None,
    start_offset: int = 0,
) -> Iterator[list[dict]]:

    params = {
        "$where": "transit_timestamp >= '2025-06-01T00:00:00'",
        "$order": (
            "transit_timestamp ASC, "
            "station_complex_id ASC, "
            "payment_method ASC, "
            "fare_class_category ASC"
        ),
    }

    yield from fetch_data_in_batches(
        endpoint=SUBWAY_ENDPOINT,
        params=params,
        batch_size=batch_size,
        max_records=max_records,
        start_offset=start_offset,
    )
