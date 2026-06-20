"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Authentication and Verification Package Initializer
"""

# Import key security and telecom functions from sub-modules
from src.auth.verification import create_and_log_otp, verify_user_otp
from src.auth.sms_gateway import send_otp_sms

# Define clean export boundaries for external application components
__all__ = [
    "create_and_log_otp",
    "verify_user_otp",
    "send_otp_sms"
]
