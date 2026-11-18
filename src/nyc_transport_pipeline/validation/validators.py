
from datetime import datetime
from decimal import Decimal, InvalidOperation


def validate_timestamp(value: str) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False

    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate_non_negative_number(value) -> bool:
    if value is None:
        return True

    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return False

    return (
        number.is_finite()
        and number >= 0
        and number == number.to_integral_value()
        and number <= Decimal("9223372036854775807")
    )


def validate_coordinate(
    value,
    minimum: Decimal,
    maximum: Decimal,
) -> bool:
    if value is None:
        return True

    try:
        coordinate = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return False

    return (
        coordinate.is_finite()
        and minimum <= coordinate <= maximum
    )


def validate_subway_record(record: dict) -> list[str]:
    errors = []

    if not isinstance(record, dict):
        return ["Record must be a dictionary"]

    if not validate_timestamp(record.get("transit_timestamp")):
        errors.append("Invalid or missing transit_timestamp")

    required_fields = [
        "station_complex_id",
        "payment_method",
        "fare_class_category",
    ]

    for field in required_fields:
        value = record.get(field)

        if not isinstance(value, str) or not value.strip():
            errors.append(f"Missing or invalid {field}")

    for field in ["ridership", "transfers"]:
        if not validate_non_negative_number(record.get(field)):
            errors.append(f"Invalid {field}")

    if not validate_coordinate(
        record.get("latitude"),
        Decimal("-90"),
        Decimal("90"),
    ):
        errors.append("Invalid latitude")

    if not validate_coordinate(
        record.get("longitude"),
        Decimal("-180"),
        Decimal("180"),
    ):
        errors.append("Invalid longitude")

    return errors


def validate_bus_record(record: dict) -> list[str]:
    errors = []

    if not isinstance(record, dict):
        return ["Record must be a dictionary"]

    if not validate_timestamp(record.get("transit_timestamp")):
        errors.append("Invalid or missing transit_timestamp")

    required_fields = [
        "bus_route",
        "payment_method",
        "fare_class_category",
    ]

    for field in required_fields:
        value = record.get(field)

        if not isinstance(value, str) or not value.strip():
            errors.append(f"Missing or invalid {field}")

    for field in ["ridership", "transfers"]:
        if not validate_non_negative_number(record.get(field)):
            errors.append(f"Invalid {field}")

    return errors
