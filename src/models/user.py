"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Data Model: Administrative Users and Role Management
"""

import logging
from config.database import get_db_cursor

logger = logging.getLogger("McjRoadSigns.Models.User")

class UserModel:
    @staticmethod
    def get_user_by_mobile(mobile_number: str) -> dict or None:
        """
        Fetches an administrative user profile using their registered mobile number.
        Used by the OTP generation system to verify if a user belongs to the municipal panel.
        """
        clean_mobile = mobile_number.strip()
        
        query = """
            SELECT user_id, mobile_number, full_name, role_level, is_active
            FROM administrative_users
            WHERE mobile_number = %s;
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (clean_mobile,))
                record = cursor.fetchone()
                
                if record:
                    return {
                        "user_id": record[0],
                        "mobile_number": record[1],
                        "full_name": record[2],
                        "role_level": record[3],  # 'SuperAdmin', 'Manager', or 'Creator'
                        "is_active": record[4]
                    }
                return None
        except Exception as error:
            logger.error(f"Failed to fetch user by mobile number {clean_mobile}: {error}")
            raise error

    @staticmethod
    def create_new_user(mobile_number: str, full_name: str, role_level: str) -> bool:
        """
        Registers a new municipal employee into the platform database.
        Restricted strictly to SuperAdmin users.
        """
        if role_level not in ['SuperAdmin', 'Manager', 'Creator']:
            raise ValueError("Invalid administrative user role level specified.")

        query = """
            INSERT INTO administrative_users (mobile_number, full_name, role_level)
            VALUES (%s, %s, %s);
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (mobile_number.strip(), full_name.strip(), role_level))
            logger.info(f"Successfully registered new system operator: {full_name} ({role_level})")
            return True
        except Exception as error:
            logger.error(f"Failed to insert new user record: {error}")
            return False
