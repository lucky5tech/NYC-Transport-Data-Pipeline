
-- ============================================
-- RAW -> STAGING: BUS HOURLY RIDERSHIP
-- ============================================

INSERT INTO staging.stg_bus_hourly_ridership (
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
    TRIM(bus_route),
    TRIM(payment_method),
    TRIM(fare_class_category),
    ridership,
    transfers,
    loaded_at
FROM raw.bus_hourly_ridership
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


-- ============================================
-- RAW -> STAGING: SUBWAY HOURLY RIDERSHIP
-- ============================================

INSERT INTO staging.stg_subway_hourly_ridership (
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
    TRIM(station_complex_id),
    NULLIF(TRIM(transit_mode), ''),
    NULLIF(TRIM(station_complex), ''),
    NULLIF(TRIM(borough), ''),
    TRIM(payment_method),
    TRIM(fare_class_category),
    ridership,
    transfers,
    latitude,
    longitude,
    loaded_at
FROM raw.subway_hourly_ridership
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
