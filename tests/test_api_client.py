import pytest
import requests

from unittest.mock import patch

from nyc_transport_pipeline.extract.api_client import fetch_data


def test_fetch_data():
    endpoint = "https://data.ny.gov/resource/5wq4-mkjj.json"

    params = {
        "$limit": 5,
    }

    data = fetch_data(endpoint, params)

    assert isinstance(data, list)
    assert len(data) == 5
    assert isinstance(data[0], dict)


def test_fetch_data_timeout():
    with patch(
        "nyc_transport_pipeline.extract.api_client.requests.get",
        side_effect=requests.exceptions.Timeout,
    ):
        with pytest.raises(RuntimeError, match="API request timed out"):
            fetch_data("https://example.com")


def test_fetch_data_connection_error():
    with patch(
        "nyc_transport_pipeline.extract.api_client.requests.get",
        side_effect=requests.exceptions.ConnectionError,
    ):
        with pytest.raises(RuntimeError, match="Failed to connect to API"):
            fetch_data("https://example.com")


def test_fetch_data_http_error():
    mock_response = requests.Response()
    mock_response.status_code = 500

    with patch(
        "nyc_transport_pipeline.extract.api_client.requests.get",
        return_value=mock_response,
    ):
        with pytest.raises(RuntimeError, match="API returned an HTTP error"):
            fetch_data("https://example.com")

def test_fetch_data_invalid_json_structure():
    mock_response = requests.Response()
    mock_response.status_code = 200

    mock_response._content = b'{"error": "Something went wrong"}'

    with patch(
        "nyc_transport_pipeline.extract.api_client.requests.get",
        return_value=mock_response,
    ):
        with pytest.raises(
            ValueError,
            match="API response must be a list",
        ):
            fetch_data("https://example.com")


def test_fetch_data_retry_success():
    endpoint = "https://example.com"

    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'[{"id": 1}, {"id": 2}]'

    with patch(
        "nyc_transport_pipeline.extract.api_client.requests.get",
        side_effect=[
            requests.exceptions.Timeout,
            requests.exceptions.Timeout,
            mock_response,
        ],
    ) as mock_get, patch(
        "nyc_transport_pipeline.extract.api_client.time.sleep"
    ) as mock_sleep:

        data = fetch_data(endpoint)

        assert data == [{"id": 1}, {"id": 2}]
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2
