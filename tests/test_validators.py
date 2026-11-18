from nyc_transport_pipeline.validation.validators import (
    validate_timestamp,
    validate_non_negative_number,
    validate_coordinate,
    validate_subway_record,
    validate_bus_record,
)

from decimal import Decimal


def test_validate_timestamp():
    assert validate_timestamp("2025-06-01T10:00:00") is True
    assert validate_timestamp("wrong-date") is False
    assert validate_timestamp("") is False


def test_validate_non_negative_number():
    assert validate_non_negative_number("150") is True
    assert validate_non_negative_number("0") is True
    assert validate_non_negative_number("10.5") is False
    assert validate_non_negative_number("-10") is False
    assert validate_non_negative_number(None) is True


def test_validate_coordinate():
    assert validate_coordinate("40.7128", Decimal("-90"), Decimal("90")) is True
    assert validate_coordinate("200", Decimal("-90"), Decimal("90")) is False
    assert validate_coordinate(None, Decimal("-90"), Decimal("90")) is True


def test_validate_subway_record():
    record = {
        "transit_timestamp": "2025-06-01T10:00:00",
        "station_complex_id": "635",
        "payment_method": "OMNY",
        "fare_class_category": "MetroCard - Full Fare",
        "ridership": "150",
        "transfers": "10",
        "latitude": "40.7128",
        "longitude": "-74.0060",
    }

    assert validate_subway_record(record) == []


def test_validate_bus_record():
    record = {
        "transit_timestamp": "2025-06-01T10:00:00",
        "bus_route": "M15",
        "payment_method": "OMNY",
        "fare_class_category": "MetroCard - Full Fare",
        "ridership": "150",
        "transfers": "10",
    }

    assert validate_bus_record(record) == []


def test_invalid_subway_record():
    record = {
        "transit_timestamp": "wrong-date",
        "ridership": "-10",
        "latitude": "200",
    }

    errors = validate_subway_record(record)

    assert len(errors) == 6
    assert "Invalid or missing transit_timestamp" in errors
    assert "Invalid ridership" in errors
    assert "Invalid latitude" in errors


def test_invalid_bus_record():
    record = {
        "transit_timestamp": "wrong-date",
        "bus_route": "",
        "ridership": "-10",
    }

    errors = validate_bus_record(record)

    assert "Invalid or missing transit_timestamp" in errors
    assert "Missing or invalid bus_route" in errors
    assert "Invalid ridership" in errors
