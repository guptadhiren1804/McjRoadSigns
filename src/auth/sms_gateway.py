"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Telecom Integration Wrapper: Flexible SMS Dispatches for OTP Verifications
"""

import os
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger("McjRoadSigns.SMSGateway")

# Pull localized environment tokens out of runtime settings profiles
SMS_GATEWAY_PROVIDER = os.getenv("SMS_GATEWAY_PROVIDER", "development").lower()
SMS_API_KEY = os.getenv("SMS_API_KEY")
SMS_SENDER_ID = os.getenv("SMS_SENDER_ID", "MCJMUN")

def send_otp_sms(mobile_number: str, raw_otp: str) -> bool:
    """
    Dispatches a standardized trilingual compliant validation text block
    to the target user smartphone utilizing configured system providers.
    """
    # Standard Indian Telecom Regulatory Authority (TRAI) explicit template text framework
    sms_text = f"[MCJ] Your secure verification pass code for McjRoadSigns dashboard access is: {raw_otp}. Valid for 3 minutes. Do not share."

    # -----------------------------------------------------------------
    # CONFIGURATION BLOCK 1: Development Sandbox Loop
    # -----------------------------------------------------------------
    if SMS_GATEWAY_PROVIDER == "development" or not SMS_API_KEY:
        logger.info("==================================================")
        logger.info("   [DEVELOPMENT MODE - SMS DISPATCH SIMULATION]   ")
        logger.info(f"   Target Phone: {mobile_number}")
        logger.info(f"   Active Token: {raw_otp}")
        logger.info("==================================================")
        return True

    # -----------------------------------------------------------------
    # CONFIGURATION BLOCK 2: Twilio API Integrations Wrapper
    # -----------------------------------------------------------------
    elif SMS_GATEWAY_PROVIDER == "twilio":
        try:
            # Twilio mandates account SID extraction embedded within the user key
            # Uses built-in urllib to keep external installation requirements down
            account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            if not account_sid:
                logger.error("Configuration Error: TWILIO_ACCOUNT_SID is missing.")
                return False
                
            twilio_url = f"https://twilio.com{account_sid}/Messages.json"
            
            payload = {
                "To": mobile_number,
                "From": SMS_SENDER_ID,  # Twilio phone number or shortcode
                "Body": sms_text
            }
            
            data = urllib.parse.urlencode(payload).encode("utf-8")
            req = urllib.request.Request(twilio_url, data=data, method="POST")
            
            # Inject HTTP Basic Authentication headers required by Twilio
            import base64
            auth_str = f"{account_sid}:{SMS_API_KEY}"
            b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            req.add_header("Authorization", f"Basic {b64_auth}")
            
            with urllib.request.urlopen(req) as response:
                if response.status in:
                    logger.info(f"Twilio cellular handoff finalized for token trace to {mobile_number}.")
                    return True
            return False
            
        except Exception as err:
            logger.error(f"Twilio communications loop broke down under execution: {err}")
            return False

    # -----------------------------------------------------------------
    # CONFIGURATION BLOCK 3: Indian Bulk SMS HTTP GET/POST API Router
    # -----------------------------------------------------------------
    elif SMS_GATEWAY_PROVIDER == "custom":
        try:
            # Standard pattern used by Indian aggregators. Modify fields to match your vendor API document.
            base_vendor_url = "https://indiansmsgateway.com"
            
            query_parameters = {
                "apikey": SMS_API_KEY,
                "sender": SMS_SENDER_ID,
                "route": "dlt_transactional", # Enforces rapid priority routing through telecom hubs
                "destination": mobile_number,
                "message": sms_text
            }
            
            # Compile key-value blocks into perfectly formatted URL safe encoding strings
            encoded_args = urllib.parse.urlencode(query_parameters)
            compiled_request_url = f"{base_vendor_url}?{encoded_args}"
            
            # Fire an asynchronous payload ping straight to the telecom vendor server
            with urllib.request.urlopen(compiled_request_url, timeout=5) as response:
                result_bytes = response.read()
                logger.info(f"Custom Indian Bulk SMS response recorded: {result_bytes.decode('utf-8')}")
                return True
                
        except Exception as err:
            logger.error(f"Custom gateway communications pipeline broke down: {err}")
            return False

    logger.critical(f"Unknown SMS_GATEWAY_PROVIDER option specified: {SMS_GATEWAY_PROVIDER}")
    return False
