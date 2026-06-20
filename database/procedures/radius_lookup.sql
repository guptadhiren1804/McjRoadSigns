_-- =====================================================================
-- MUNICIPAL CORPORATION JALANDHAR ROAD SIGNS PROJECT (McjRoadSigns)
-- SPATIAL PROCEDURAL FUNCTION: NEAREST SIGN BOARDS RADIUS LOOKUP
-- =====================================================================

CREATE OR REPLACE FUNCTION get_signs_within_radius_meters(
    user_longitude DOUBLE PRECISION,
    user_latitude DOUBLE PRECISION,
    radius_meters DOUBLE PRECISION
)
RETURNS TABLE (
    instance_id INT,
    sign_uid VARCHAR(50),
    irc_sign_code VARCHAR(30),
    title_en VARCHAR(255),
    distance_meters DOUBLE PRECISION,
    geom_text TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.instance_id,
        i.sign_uid,
        m.irc_sign_code,
        p.title_en,
        -- ST_Distance calculates geography parameters as meters natively using geography casts
        ST_Distance(
            i.geo_location::geography, 
            ST_SetSRID(ST_MakePoint(user_longitude, user_latitude), 4326)::geography
        ) AS distance_meters,
        ST_AsText(i.geo_location) AS geom_text
    FROM sign_instances i
    JOIN sign_masters m ON i.master_id = m.master_id
    JOIN sign_landing_pages p ON i.sign_uid = p.sign_uid
    WHERE ST_DWithin(
        i.geo_location::geography, 
        ST_SetSRID(ST_MakePoint(user_longitude, user_latitude), 4326)::geography, 
        radius_meters
    )
    ORDER BY distance_meters ASC;
END;
$$ LANGUAGE plpgsql;
