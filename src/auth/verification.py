"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Secure OTP Generation and Verification Operations
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
import logging
from config.database import get_db_cursor

logger = logging.getLogger("McjRoadSigns.Verification")

# Set strict OTP lifetime constraint to prevent replay attacks
OTP_EXPIRY_MINUTES = 3

def generate_secure_otp() -> str:
    """
    Generates a cryptographically secure 6-digit numeric token.
    Never use standard 'random.randint' for municipal authentication safety.
    """
    return "".join(secrets.choice("0123456789") for _ in range(6))

def hash_otp(otp: str) -> str:
    """
    Hashes the OTP token text using the SHA-256 algorithm.
    This prevents plaintext codes from living inside database logs.
    """
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()

def create_and_log_otp(mobile_number: str) -> str:
    """
    Generates a secure OTP, saves its hash to the database, 
    and returns the raw string to be dispatched via SMS gateway.
    """
    raw_otp = generate_secure_otp()
    hashed_otp = hash_otp(raw_otp)
    
    # Establish precise localized expiry window limits
    expiry_time = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    query = """
        INSERT INTO otp_logs (mobile_number, otp_hash, expires_at)
        VALUES (%s, %s, %s);
    """
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query, (mobile_number, hashed_otp, expiry_time))
        logger.info(f"Secure OTP token hash logged successfully for user destination phone.")
        return raw_otp
    except Exception as error:
        logger.error(f"Failed to log security token inside authentication ledger: {error}")
        raise error

def verify_user_otp(mobile_number: str, user_input_otp: str) -> bool:
    """
    Looks up database logs to verify if the provided OTP matches 
    the active unexpired record for that specific mobile number.
    """
    hashed_input = hash_otp(user_input_otp)
    current_time = datetime.now(timezone.utc)
    
    # Query to extract only unverified and active tokens matching criteria
    select_query = """
        SELECT otp_id FROM otp_logs
        WHERE mobile_number = %s 
          AND otp_hash = %s 
          AND is_verified = FALSE 
          AND expires_at > %s
        ORDER BY created_at DESC 
        LIMIT 1;
    """
    
    update_query = """
        UPDATE otp_logs 
        SET is_verified = TRUE 
        WHERE otp_id = %s;
    """
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute(select_query, (mobile_number, hashed_input, current_time))
            record = cursor.fetchone()
            
            if record:
                # cursor.fetchone() returns a tuple; extract primary key ID directly
                otp_id = record[0]
                
                # Consume token instantly so it can never be processed a second time
                cursor.execute(update_query, (otp_id,))
                logger.info(f"OTP verification successful. Token consumed for security bounds.")
                return True
                
        logger.warning(f"Failed authentication challenge attempt logged for number context.")
        return False
        
    except Exception as error:
        logger.error(f"Internal database tracking error handling token verification challenge: {error}")
        return False
