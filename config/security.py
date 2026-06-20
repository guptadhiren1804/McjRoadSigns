"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Core Security and Cryptographic Validation Utilities
"""

import re
import logging

logger = logging.getLogger("McjRoadSigns.Security")

# Regex to enforce your secure random URL structure pattern (e.g., MCJ-0021-X7R2)
# Matches: base prefix code - numbers sequence - 4 character alphanumeric random tag
SECURE_URL_PATTERN = re.compile(r"^[A-Z0-9]+-[0-9]+-[2-9A-H_J-N_P-Z]{4}$")

def validate_secure_url_token(sign_uid: str) -> bool:
    """
    Checks incoming scanned tracking parameters against structural boundaries.
    Blocks malformed parameters to defend against injection or database parsing attacks.
    """
    if not sign_uid:
        return False
        
    clean_token = sign_uid.strip().upper()
    
    # Evaluate structural string layout metrics
    if SECURE_URL_PATTERN.match(clean_token):
        return True
        
    logger.warning(f"SECURITY MALWARE BLOCKED: Scanned token failed structural Regex verification: {sign_uid}")
    return False
