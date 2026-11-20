-- Bus: STAGING -> ANALYTICS
INSERT INTO analytics.fact_bus_hourly_ridership (
    transit_timestamp,
    bus_route,
    payment_method,
    fare_class_category,
    ridership,
    transfers,
    loaded_at
)
SELECT
    transit_timestamp,
    bus_route,
    payment_method,
    fare_class_category,
    ridership,
    transfers,
    loaded_at
FROM staging.stg_bus_hourly_ridership
ON CONFLICT (
    transit_timestamp,
    bus_route,
    payment_method,
    fare_class_category
)
DO UPDATE SET
    ridership = EXCLUDED.ridership,
    transfers = EXCLUDED.transfers,
    loaded_at = EXCLUDED.loaded_at;


-- Subway: STAGING -> ANALYTICS
INSERT INTO analytics.fact_subway_hourly_ridership (
    transit_timestamp,
    station_complex_id,
    transit_mode,
    station_complex,
    borough,
    payment_method,
    fare_class_category,
    ridership,
    transfers,
    latitude,
    longitude,
    loaded_at
)
SELECT
    transit_timestamp,
    station_complex_id,
    transit_mode,
    station_complex,
    borough,
    payment_method,
    fare_class_category,
    ridership,
    transfers,
    latitude,
    longitude,
    loaded_at
FROM staging.stg_subway_hourly_ridership
ON CONFLICT (
    transit_timestamp,
    station_complex_id,
    payment_method,
    fare_class_category
)
DO UPDATE SET
    transit_mode = EXCLUDED.transit_mode,
    station_complex = EXCLUDED.station_complex,
    borough = EXCLUDED.borough,
    ridership = EXCLUDED.ridership,
    transfers = EXCLUDED.transfers,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    loaded_at = EXCLUDED.loaded_at;