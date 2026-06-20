"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Public Web Layer: High-Performance Routing for Citizen QR Scans
"""

import logging
from src.models.sign import SignModel

logger = logging.getLogger("McjRoadSigns.Web.Public")

def handle_citizen_scan(sign_uid: str, requested_lang: str = "en") -> dict:
    """
    Core request router for public QR scans.
    Intercepts the unguessable unique token from the URL, calls the model to pull
    the data, and prepares the layout context for the trilingual page template.
    """
    clean_uid = sign_uid.strip().upper()
    
    # 1. Fetch data parameters out of our normalized relational schema map loops
    sign_data = SignModel.get_public_landing_data(clean_uid)
    
    # Safety Boundary Checkpoint: Handled if tracking tokens are broken or guessed wrong
    if not sign_data:
        logger.warning(f"Scan request rejected: Invalid or unapproved asset ID token: {clean_uid}")
        return {
            "template": "citizen/error_404.html",
            "context": {"message": "Invalid road sign configuration or pending municipal verification approval."}
        }

    # 2. Safely unpack our open-ended dynamic JSON data canvas object
    content_map = sign_data["content"]
    
    # 3. Dynamic Trilingual Language Mapping Engine
    if requested_lang == "pa":
        display_title = sign_data["title_pa"]
        display_description = content_map.get("description_pa", content_map.get("description_en", "Content not available in Punjabi."))
    elif requested_lang == "hi":
        display_title = sign_data["title_hi"]
        display_description = content_map.get("description_hi", content_map.get("description_en", "Content not available in Hindi."))
    else:
        # Default Fallback Application State: English Mapping Configurations
        display_title = sign_data["title_en"]
        display_description = content_map.get("description_en", "Description field empty.")

    logger.info(f"Citizen scan processed successfully for reference tracker token: {clean_uid} [{requested_lang.upper()}]")
    
    # 4. Returns structured payload variables to map directly onto HTML templates
    return {
        "template": "citizen/landing_view.html",
        "context": {
            "sign_uid": clean_uid,
            "current_lang": requested_lang,
            "page_title": display_title,
            "description": display_description,
            "gallery_images": content_map.get("gallery_images", []),
            "audio_guide_url": content_map.get("audio_guide_url", None),
            "emergency_contacts": content_map.get("emergency_contacts", {"police": "112", "medical": "108"}),
            "vendor_name": sign_data["vendor_name"],
            "vendor_url": sign_data["vendor_url"],
            "attribution_text": sign_data["vendor_footer"]
        }
    }
