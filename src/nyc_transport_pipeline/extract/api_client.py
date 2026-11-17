import requests
import time
from nyc_transport_pipeline.logger import setup_logger


logger = setup_logger("extract")




def fetch_data(
    endpoint: str,
    params: dict | None = None,
    offset: int = 0,
    max_retries: int = 3,
) -> list[dict]:

    logger.info(
        "Starting API request: %s | offset=%s",
        endpoint,
        offset,
    )

    request_params = params.copy() if params else {}
    request_params["$offset"] = offset

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                endpoint,
                params=request_params,
                timeout=(60, 120),
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list):
                logger.error("API response has an invalid structure")
                raise ValueError("API response must be a list")

            logger.info(
                "Successfully received %s records | offset=%s",
                len(data),
                offset,
            )

            return data

        except requests.exceptions.Timeout as error:
            logger.warning(
                "API timeout | offset=%s | attempt=%s/%s",
                offset,
                attempt,
                max_retries,
            )

            if attempt == max_retries:
                logger.error(
                    "API timeout after all retries | offset=%s",
                    offset,
                )
                raise RuntimeError("API request timed out") from error

        except requests.exceptions.ConnectionError as error:
            logger.warning(
                "API connection error | offset=%s | attempt=%s/%s",
                offset,
                attempt,
                max_retries,
            )

            if attempt == max_retries:
                logger.error(
                    "API connection failed after all retries | offset=%s",
                    offset,
                )
                raise RuntimeError("Failed to connect to API") from error

        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code

            if status_code in (500, 502, 503, 504):
                logger.warning(
                    "Temporary API server error %s | offset=%s | attempt=%s/%s",
                    status_code,
                    offset,
                    attempt,
                    max_retries,
                )

                if attempt == max_retries:
                    logger.error(
                        "API server error after all retries | offset=%s",
                        offset,
                    )
                    raise RuntimeError("API returned an HTTP error") from error

            else:
                logger.error(
                    "Non-retryable HTTP error %s | offset=%s",
                    status_code,
                    offset,
                )
                raise RuntimeError("API returned an HTTP error") from error

        except requests.exceptions.JSONDecodeError as error:
            logger.error(
                "API returned invalid JSON | offset=%s",
                offset,
            )
            raise RuntimeError("API returned invalid JSON") from error

        if attempt < max_retries:
            delay = 2 ** attempt

            logger.info(
                "Retrying API request in %s seconds | offset=%s",
                delay,
                offset,
            )

            time.sleep(delay)

    raise RuntimeError("API request failed")




def fetch_data_in_batches(
    endpoint: str,
    params: dict | None = None,
    batch_size: int = 50000,
    max_records: int | None = None,
    start_offset: int = 0,
):
    offset = start_offset
    total_records = 0

    while max_records is None or total_records < max_records:
        current_limit = batch_size

        if max_records is not None:
            remaining = max_records - total_records
            current_limit = min(batch_size, remaining)

        request_params = params.copy() if params else {}
        request_params["$limit"] = current_limit

        batch = fetch_data(
            endpoint,
            params=request_params,
            offset=offset,
        )

        if not batch:
            break

        yield batch

        total_records += len(batch)
        offset += len(batch)

        if len(batch) < current_limit:
            break
