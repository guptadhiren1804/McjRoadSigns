"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Administrative Web Layer: Structured Content Uploads, Approvals, and Random Asset Pipelines
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
    Executes the secure pipeline required to deploy a new asset into 3 tables.
    Gracefully normalizes row tuples into standard tracking variables.
    """
    # 1. Enforce Role/Session validation
    if not enforce_admin_session_guard(session_user):
        return {"status": "error", "code": 403, "message": "Access Denied: Insufficient permissions."}

    # 2. AUTOMATIC TUPLE NORMALIZATION MATRIX
    if isinstance(session_user, (tuple, list)):
        user_id = session_user[0]
        user_role = session_user[3]
    else:
        user_id = session_user.get("user_id")
        user_role = session_user.get("role_level")
    
    # Extract structural specifications from web form data
    master_id = int(form_data.get("master_id"))
    longitude = float(form_data.get("longitude", 0.0))
    latitude = float(form_data.get("latitude", 0.0))
    
    title_en = sanitize_input_text(form_data.get("title_en", "Pending Initialization"))
    title_pa = sanitize_input_text(form_data.get("title_pa", "ਲੰਬਿਤ ਮੈਪਿੰਗ"))
    title_hi = sanitize_input_text(form_data.get("title_hi", "लंबित मैपिंग"))

    if not master_id:
        return {"status": "error", "code": 400, "message": "Missing core sign master template ID."}

    # ─── ENSURE THIS TRY BLOCK IS INDENTED EXACTLY 4 SPACES IN ───
    try:
        with get_db_cursor() as cursor:
            # Step 1: Let the generator yield a secure, random 10-character token string
            qr_metadata = generate_sign_qr_asset(cursor)
            generated_uid = qr_metadata["sign_uid"]
            
            # Step 2: [TABLE 1 INSERT] Plot physical post instance down into PostGIS map layer using verified user_id
            insert_instance_query = """
                INSERT INTO sign_instances (master_id, sign_uid, geo_location, created_by)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
                RETURNING id;
            """
            cursor.execute(insert_instance_query, (master_id, generated_uid, longitude, latitude, user_id))
            instance_id = cursor.fetchone()[0] # Safely unwrap returning scalar integer value
            
            # Step 3: [TABLE 2 INSERT] Track static digital file mounts in storage directory
            insert_assets_query = """
                INSERT INTO sign_digital_assets (sign_instance_id, qr_vector_path, print_pdf_path)
                VALUES (%s, %s, %s);
            """
            qr_vector_path = f"storage/qr_vectors/{generated_uid}.svg"
            print_pdf_path = f"storage/sign_pdfs/{generated_uid}.pdf"
            cursor.execute(insert_assets_query, (instance_id, qr_vector_path, print_pdf_path))
            
            # Step 4: [TABLE 3 INSERT] Spawn the matching isolated landing page profile canvas record
            initial_content_payload = {
                "description_en": "Welcome to Jalandhar Smart City Infrastructure. Detailed content initialized by Ferrum Tech Industries.",
                "description_pa": "ਜਲੰਧਰ ਸਮਾਰਟ ਸਿਟੀ ਬੁਨਿਆਦੀ ਢਾਂਚੇ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ।",
                "description_hi": "जालंधर स्मार्ट सिटी बुनियादी ढांचे में आपका स्वागत है।",
                "gallery_images": [], 
                "audio_guide_url": None,
                "emergency_contacts": {"police": "112", "medical": "108"}
            }
            
            insert_landing_query = """
                INSERT INTO sign_landing_pages (sign_uid, title_en, title_pa, title_hi, content_json, updated_by)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(insert_landing_query, (generated_uid, title_en, title_pa, title_hi, json.dumps(initial_content_payload), user_id))

        # Step 5: Stitch the crisp QR vector straight into the final printable asset sheet
        compile_print_pdf(qr_metadata)

        logger.info(f"System initialization lifecycle completed for asset board: {generated_uid}")
        return {
            "status": "success",
            "message": "Sign asset deployed on map layout across all 3 registries. Printable PDF compiled successfully.",
            "sign_uid": generated_uid,
            "paths": {
                "svg": qr_vector_path,
                "pdf": print_pdf_path
            }
        }

    except Exception as error:
        logger.error(f"Asset pipeline broken down during sign deployment execution: {error}")
        return {"status": "error", "code": 500, "message": "Internal processing failure running generator pipeline."}



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
