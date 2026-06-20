"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Administrative Web Layer: Decoupled Asset Deployment & Dynamic Table Linkage Runtimes
"""

import json
import logging
from config.database import get_db_cursor
from src.web.middleware import sanitize_input_text, enforce_admin_session_guard
from src.core.qr_generator import generate_sign_qr_asset
from src.core.pdf_compiler import compile_print_pdf

logger = logging.getLogger("McjRoadSigns.Web.Admin")

def handle_create_new_sign_board(form_data: dict, session_user: dict) -> dict:
    """
    Deploys a new IRC:67 asset board, inserting an isolated entry into sign_instances only.
    Coordinates default to NULL if not physically installed yet.
    """
    if not enforce_admin_session_guard(session_user):
        return {"status": "error", "code": 403, "message": "Access Denied: Insufficient permissions."}

    # Normalize user tracking variables from tuple context structures safely
    if isinstance(session_user, (tuple, list)):
        user_id = session_user[0]
    else:
        user_id = session_user.get("user_id")
        
    master_id = int(form_data.get("master_id", 0))
    if not master_id:
        return {"status": "error", "code": 400, "message": "Missing core sign master template ID."}

    # Parse coordinates flexibly. If missing, 0, or blank, store as None (NULL in DB)
    lon_raw = form_data.get("longitude")
    lat_raw = form_data.get("latitude")
    
    try:
        longitude = float(lon_raw) if lon_raw and float(lon_raw) != 0.0 else None
        latitude = float(lat_raw) if lat_raw and float(lat_raw) != 0.0 else None
    except ValueError:
        longitude, latitude = None, None

    try:
        with get_db_cursor() as cursor:
            # Generate your streamlined clean 10-character unique token identifier string
            qr_metadata = generate_sign_qr_asset(cursor)
            generated_uid = qr_metadata["sign_uid"]
            
            # Conditionally map PostGIS spatial parameters based on data availability
            if longitude is not None and latitude is not None:
                insert_instance_query = """
                    INSERT INTO sign_instances (master_id, sign_uid, geo_location, created_by)
                    VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
                    RETURNING id;
                """
                cursor.execute(insert_instance_query, (master_id, generated_uid, longitude, latitude, user_id))
            else:
                # Deploying to warehouse state prior to physical field placement mapping
                insert_instance_query = """
                    INSERT INTO sign_instances (master_id, sign_uid, geo_location, created_by)
                    VALUES (%s, %s, NULL, %s)
                    RETURNING id;
                """
                cursor.execute(insert_instance_query, (master_id, generated_uid, user_id))
                
            instance_id = cursor.fetchone()[0]

        logger.info(f"Sign instance allocated in manufacturing registry queue: ID {instance_id} | Token: {generated_uid}")
        return {
            "status": "success",
            "message": f"Sign board entry deployed successfully under Token {generated_uid}. Coordinates left unmapped.",
            "sign_uid": generated_uid,
            "instance_id": instance_id
        }

    except Exception as error:
        logger.error(f"Asset deployment pipeline broken down: {error}")
        return {"status": "error", "code": 500, "message": "Internal processing failure running generator pipeline."}


def handle_link_digital_asset_to_instance(form_data: dict, session_user: dict) -> dict:
    """
    Dynamically maps or switches a Digital Asset profile row pointer to a different Sign Instance ID.
    """
    if not enforce_admin_session_guard(session_user):
        return {"status": "error", "code": 403, "message": "Unauthorized context action access."}

    digital_asset_id = int(form_data.get("digital_asset_id", 0))
    target_instance_id = int(form_data.get("target_instance_id", 0))

    if not digital_asset_id or not target_instance_id:
        return {"status": "error", "code": 400, "message": "Missing necessary linkage reference targets."}

    update_query = """
        UPDATE sign_digital_assets
        SET sign_instance_id = %s
        WHERE id = %s;
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(update_query, (target_instance_id, digital_asset_id))
        logger.info(f"Digital asset id {digital_asset_id} re-linked to sign instance id {target_instance_id}")
        return {"status": "success", "message": "Digital Asset layout linked to new target sign board instance successfully."}
    except Exception as error:
        logger.error(f"Linkage manipulation failed: {error}")
        return {"status": "error", "code": 500, "message": "Database transaction failure recording asset linkage adjustment."}


def handle_link_landing_page_to_instance(form_data: dict, session_user: dict) -> dict:
    """
    Dynamically transfers a Canvas Landing Page profile record link over to a different unique tracking sign_uid string.
    """
    if not enforce_admin_session_guard(session_user):
        return {"status": "error", "code": 403, "message": "Unauthorized action access context."}

    landing_page_id = int(form_data.get("landing_page_id", 0))
    target_sign_uid = sanitize_input_text(form_data.get("target_sign_uid", "")).strip().upper()

    if not landing_page_id or not target_sign_uid:
        return {"status": "error", "code": 400, "message": "Missing core page identification mapping targets."}

    update_query = """
        UPDATE sign_landing_pages
        SET sign_uid = %s
        WHERE id = %s;
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(update_query, (target_sign_uid, landing_page_id))
        logger.info(f"Landing page id {landing_page_id} successfully bound over to sign token: {target_sign_uid}")
        return {"status": "success", "message": f"Landing page layout linked over to target sign token reference {target_sign_uid} successfully."}
    except Exception as error:
        logger.error(f"Landing page re-routing allocation configuration dropped: {error}")
        return {"status": "error", "code": 500, "message": "Database transaction error mutating landing portal mapping values."}



def handle_update_content_payload(form_data: dict, session_user: dict) -> dict:
    """Facilitates dynamic web text updates into content_json columns."""
    if not enforce_admin_session_guard(session_user):
        return {"status": "error", "code": 403, "message": "Unauthorized context action access."}

    user_id = session_user.get("user_id")
    user_role = session_user.get("role_level")
    sign_uid = sanitize_input_text(form_data.get("sign_uid"))
    
    title_en = sanitize_input_text(form_data.get("title_en"))
    title_pa = sanitize_input_text(form_data.get("title_pa"))
    title_hi = sanitize_input_text(form_data.get("title_hi"))
    
    compiled_payload = {
        "description_en": sanitize_input_text(form_data.get("description_en", "")),
        "description_pa": sanitize_input_text(form_data.get("description_pa", "")),
        "description_hi": sanitize_input_text(form_data.get("description_hi", "")),
        "gallery_images": form_data.get("images_list", []),
        "audio_guide_url": form_data.get("audio_url", None),
        "emergency_contacts": {
            "police": sanitize_input_text(form_data.get("phone_police", "112")),
            "medical": sanitize_input_text(form_data.get("phone_medical", "108"))
        }
    }

    approval_reset_state = True if user_role in ["SuperAdmin", "Manager"] else False

    update_query = """
        UPDATE sign_landing_pages
        SET title_en = %s, title_pa = %s, title_hi = %s, content_json = %s, 
            is_approved = %s, updated_by = %s, updated_at = CURRENT_TIMESTAMP
        WHERE sign_uid = %s;
    """

    try:
        with get_db_cursor() as cursor:
            cursor.execute(update_query, (title_en, title_pa, title_hi, json.dumps(compiled_payload), approval_reset_state, user_id, sign_uid))
        logger.info(f"Trilingual payload modifications saved for token reference: {sign_uid}")
        return {"status": "success", "message": "Edits committed to database. Awaiting manager approval."}
    except Exception as error:
        logger.error(f"Failed to update landing contents: {error}")
        return {"status": "error", "code": 500, "message": "Database transaction failure recording text blocks."}


def handle_manager_approval_toggle(sign_uid: str, session_user: dict) -> dict:
    """Enforces the final checkpoint loop step. Pushes a pending page to public view live."""
    if not enforce_admin_session_guard(session_user):
        return {"status": "error", "code": 403, "message": "Access Denied."}

    user_role = session_user.get("role_level")
    user_id = session_user.get("user_id")

    if user_role not in ["SuperAdmin", "Manager"]:
        return {"status": "error", "code": 403, "message": "Security policy violation: Creators cannot self-approve content."}

    clean_uid = sign_uid.strip().upper()
    approval_query = """
        UPDATE sign_landing_pages
        SET is_approved = TRUE, approved_by = %s, updated_at = CURRENT_TIMESTAMP
        WHERE sign_uid = %s;
    """

    try:
        with get_db_cursor() as cursor:
            cursor.execute(approval_query, (user_id, clean_uid))
        logger.info(f"Verification finalized. Landing portal profile pushed live for token: {clean_uid}")
        return {"status": "success", "message": f"Sign landing page {clean_uid} is now officially active and public."}
    except Exception as error:
        logger.error(f"Approval toggle failed: {error}")
        return {"status": "error", "code": 500, "message": "Database system error logging approval status step."}
