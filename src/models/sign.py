"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Data Model Logic: Core Signs Queries and Relational Joins
"""

import json
import logging
from config.database import get_db_cursor

logger = logging.getLogger("McjRoadSigns.Models.Sign")

class SignModel:
    @staticmethod
    def get_public_landing_data(sign_uid: str) -> dict or None:
        """
        Executes a high-performance join query to fetch trilingual page layout content 
        and corporate vendor branding footer data when an end-user scans a QR code.
        Only fetches pages where is_approved = TRUE.
        """
        clean_uid = sign_uid.strip().upper()
        
        query = """
            SELECT 
                p.title_en, p.title_pa, p.title_hi, p.content_json,
                v.company_name, v.corporate_url, v.attribution_text_en
            FROM sign_landing_pages p
            JOIN sign_instances i ON p.sign_uid = i.sign_uid
            JOIN vendor_branding_profiles v ON p.vendor_profile_id = v.profile_id
            WHERE p.sign_uid = %s AND p.is_approved = TRUE;
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (clean_uid,))
                record = cursor.fetchone()
                
                if record:
                    return {
                        "title_en": record[0],
                        "title_pa": record[1],
                        "title_hi": record[2],
                        "content": record[3],       # Native dictionary unpacked from JSONB
                        "vendor_name": record[4],
                        "vendor_url": record[5],
                        "vendor_footer": record[6]
                    }
                return None
        except Exception as error:
            logger.error(f"Database query failed to fetch landing data for UID {clean_uid}: {error}")
            raise error

    @staticmethod
    def create_new_sign_instance(master_id: int, sign_uid: str, longitude: float, latitude: float, user_id: int) -> bool:
        """
        Registers a new physical sign post instance onto the PostGIS layer.
        Coordinates are passed as floats and compiled into an ST_MakePoint geometry structure.
        """
        clean_uid = sign_uid.strip().upper()
        
        # ST_SetSRID maps the coordinates to the standard WGS84 GPS world map (4326)
        query = """
            INSERT INTO sign_instances (master_id, sign_uid, geo_location, created_by)
            VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s);
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (master_id, clean_uid, longitude, latitude, user_id))
            logger.info(f"Physical asset post plotted on PostGIS map layer: {clean_uid}")
            return True
        except Exception as error:
            logger.error(f"Failed to insert physical asset instance row for {clean_uid}: {error}")
            return False

    @staticmethod
    def get_sign_by_uid(sign_uid: str) -> dict or None:
        """
        Fetches an administrative snapshot of an existing sign layout.
        Used by creators and managers within the backend portal.
        """
        clean_uid = sign_uid.strip().upper()
        
        query = """
            SELECT page_id, sign_uid, title_en, title_pa, title_hi, content_json, is_approved
            FROM sign_landing_pages
            WHERE sign_uid = %s;
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (clean_uid,))
                record = cursor.fetchone()
                
                if record:
                    return {
                        "page_id": record[0],
                        "sign_uid": record[1],
                        "title_en": record[2],
                        "title_pa": record[3],
                        "title_hi": record[4],
                        "content_json": record[5],
                        "is_approved": record[6]
                    }
                return None
        except Exception as error:
            logger.error(f"Failed to query sign metadata for admin panel: {error}")
            raise error
