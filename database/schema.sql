-- =====================================================================
-- MUNICIPAL CORPORATION JALANDHAR ROAD SIGNS PROJECT (McjRoadSigns)
-- PRODUCTION DATABASE BLUEPRINT - FULL TRILINGUAL & IRC:67-2022 COMPLIANT
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- ---------------------------------------------------------------------
-- 1. ENUMERATIONS & ROLES (IRC:67-2022 Class Hierarchy)
-- ---------------------------------------------------------------------
CREATE TYPE irc_sign_class AS ENUM (
    'MandatoryOrRegulatory', 
    'CautionaryOrWarning', 
    'InformatoryOrGuide'
);

CREATE TYPE subclass_mandatory_regulatory AS ENUM (
    'RightOfWay', 'ProhibitoryRegulation', 'NoParkingNoStopping', 
    'OperationalControl', 'SpeedLimit', 'VehicleControl', 
    'RestrictionEnds', 'CompulsoryDirectionControl', 'GetawaySigns'
);

CREATE TYPE subclass_cautionary_warning AS ENUM (
    'Triangle', 'Chevron', 'Hazard'
);

CREATE TYPE subclass_informatory_guide AS ENUM (
    'FacilityInformation', 'DirectionInformation', 'PlaceIdentification', 
    'OtherUsefulInformation', 'ParkingSigns', 'FloodGauge', 
    'AdvancedDirectionSigns', 'ReassuranceSignOrRouteConfirmatory', 
    'TruckLayBay', 'TollBoothAhead', 'WeighBridgeAhead', 
    'TourismRelatedSigns', 'SignsForPWD', 'EnforcementSigns'
);

CREATE TYPE irc_sign_shape AS ENUM ('Circle', 'Triangle', 'Square', 'Rectangular', 'Octagon');
CREATE TYPE user_role_type AS ENUM ('SuperAdmin', 'Manager', 'Creator');

-- ---------------------------------------------------------------------
-- 2. USER MANAGEMENT & ACCESS CONTROL
-- ---------------------------------------------------------------------
CREATE TABLE administrative_users (
    user_id SERIAL PRIMARY KEY,
    mobile_number VARCHAR(15) UNIQUE NOT NULL, 
    full_name VARCHAR(100) NOT NULL,
    role_level user_role_type NOT NULL DEFAULT 'Creator',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_mobile ON administrative_users(mobile_number);

CREATE TABLE otp_logs (
    otp_id SERIAL PRIMARY KEY,
    mobile_number VARCHAR(15) NOT NULL,
    otp_hash VARCHAR(64) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_otp_lookup ON otp_logs(mobile_number, is_verified, expires_at);

-- ---------------------------------------------------------------------
-- 3. VENDOR/COMPANY BRANDING PROFILE CONFIGURATION
-- ---------------------------------------------------------------------
CREATE TABLE vendor_branding_profiles (
    profile_id SERIAL PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,            
    corporate_url VARCHAR(255) NOT NULL,           
    logo_image_path VARCHAR(512),                  
    attribution_text_en VARCHAR(255) NOT NULL,     
    is_default_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 4. SIGN MASTERS TABLE (Manufacturing Blueprints & IRC Enforcements)
-- ---------------------------------------------------------------------
CREATE TABLE sign_masters (
    master_id SERIAL PRIMARY KEY,
    master_code VARCHAR(100) UNIQUE NOT NULL,      
    irc_category irc_sign_class NOT NULL,          
    irc_subclass_mandatory subclass_mandatory_regulatory, 
    irc_subclass_cautionary subclass_cautionary_warning,  
    irc_subclass_informatory subclass_informatory_guide,   
    irc_sign_code VARCHAR(30) NOT NULL,             
    sign_shape irc_sign_shape NOT NULL,            
    size_width_mm INT NOT NULL,                    
    size_height_mm INT NOT NULL,                   
    
    CONSTRAINT check_subclass_integrity CHECK (
        (irc_category = 'MandatoryOrRegulatory' AND irc_subclass_mandatory IS NOT NULL AND irc_subclass_cautionary IS NULL AND irc_subclass_informatory IS NULL) OR
        (irc_category = 'CautionaryOrWarning' AND irc_subclass_cautionary IS NOT NULL AND irc_subclass_mandatory IS NULL AND irc_subclass_informatory IS NULL) OR
        (irc_category = 'InformatoryOrGuide' AND irc_subclass_informatory IS NOT NULL AND irc_subclass_mandatory IS NULL AND irc_subclass_cautionary IS NULL)
    ),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------------------
-- 5. SIGN DIGITAL ASSETS TABLE (The Cryptographic & Print File Ledger)
-- ---------------------------------------------------------------------
CREATE TABLE sign_digital_assets (
    asset_id SERIAL PRIMARY KEY,
    sign_uid VARCHAR(50) UNIQUE NOT NULL,          
    short_routing_url VARCHAR(255) UNIQUE NOT NULL,
    qr_image_path VARCHAR(512) NOT NULL,           
    print_pdf_path VARCHAR(512) NOT NULL,          
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_digital_assets_uid ON sign_digital_assets(sign_uid);

-- ---------------------------------------------------------------------
-- 6. SIGN INSTANCES TABLE (Physical Ground Deployments + GIS Plotting)
-- ---------------------------------------------------------------------
CREATE TABLE sign_instances (
    instance_id SERIAL PRIMARY KEY,
    master_id INT REFERENCES sign_masters(master_id) ON DELETE RESTRICT NOT NULL,
    sign_uid VARCHAR(50) UNIQUE REFERENCES sign_digital_assets(sign_uid) ON DELETE RESTRICT NOT NULL,
    geo_location GEOMETRY(Point, 4326) NOT NULL,   
    created_by INT REFERENCES administrative_users(user_id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_instances_spatial ON sign_instances USING GIST(geo_location);

-- ---------------------------------------------------------------------
-- 7. SIGN LANDING PAGES TABLE (Trilingual Mobile Content + Corporate Link)
-- ---------------------------------------------------------------------
CREATE TABLE sign_landing_pages (
    page_id SERIAL PRIMARY KEY,
    sign_uid VARCHAR(50) UNIQUE REFERENCES sign_digital_assets(sign_uid) ON DELETE CASCADE NOT NULL,
    vendor_profile_id INT REFERENCES vendor_branding_profiles(profile_id) ON DELETE SET NULL DEFAULT 1,
    
    -- Trilingual Title Support for Front-End Dropdown Menus
    title_en VARCHAR(255) NOT NULL,               -- English Header
    title_pa VARCHAR(255) NOT NULL,               -- Punjabi Header
    title_hi VARCHAR(255) NOT NULL,               -- Hindi Header
    
    -- Dynamic JSON canvas structured to hold nested trilingual data variants
    content_json JSONB NOT NULL,                   
    
    -- Verification Lifecycle
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    approved_by INT REFERENCES administrative_users(user_id),
    updated_by INT REFERENCES administrative_users(user_id) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_landing_pages_uid ON sign_landing_pages(sign_uid);

-- ---------------------------------------------------------------------
-- 8. SYSTEM AUDIT TRAIL
-- ---------------------------------------------------------------------
CREATE TABLE operational_audit_logs (
    audit_id SERIAL PRIMARY KEY,
    target_table VARCHAR(50) NOT NULL,             
    record_id INT NOT NULL,                        
    user_id INT REFERENCES administrative_users(user_id) ON DELETE SET NULL,
    action_performed VARCHAR(50) NOT NULL,         
    old_value_json JSONB,
    new_value_json JSONB,
    ip_address VARCHAR(45) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_lookup ON operational_audit_logs(target_table, record_id, timestamp);
