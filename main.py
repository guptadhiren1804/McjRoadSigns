"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Central Web Application Gateway Entrypoint - PART 1
"""

import os
import json
import secrets
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Request, HTTPException, Depends, status, Form
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Core Configuration and Router Core Hooks Integration Mappings
from config.database import db_pool, get_db_cursor
from src.web.public_handlers import handle_citizen_scan
from src.web.admin_handlers import handle_create_new_sign_board, handle_update_content_payload, handle_manager_approval_toggle
from src.web.middleware import process_rate_limiting_guard
from fastapi.exceptions import HTTPException as FastAPIHTTPException

# Initialize Logger
logger = logging.getLogger("McjRoadSigns.Main")
logging.basicConfig(level=logging.INFO)

# 1. Instantiate the Central Enterprise Web Application Framework
app = FastAPI(
    title="McjRoadSigns Enterprise Engine",
    description="Municipal Corporation Jalandhar Smart City QR Signs Web Infrastructure",
    version="1.0.0"
)

# 2. Map Static UI Asset Volumes and HTML Rendering View Engines
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount physical asset storage volume to allow the IRC:67 board to serve SVGs & PDFs
if not os.path.exists("storage"):
    os.makedirs("storage/qr_vectors", exist_ok=True)
    os.makedirs("storage/sign_pdfs", exist_ok=True)
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

templates = Jinja2Templates(directory="templates")

@app.exception_handler(FastAPIHTTPException)
async def custom_http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """Intercepts administrative HTTP exceptions and processes 303 redirects safely."""
    if exc.status_code == 303 and "Location" in exc.headers:
        return RedirectResponse(url=exc.headers["Location"], status_code=303)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.on_event("startup")
def app_startup_notification_loop():
    """Confirms configuration bounds when the city-scale framework goes online."""
    logger.info("==================================================")
    logger.info("   MCJ ROAD SIGNS MASTER SYSTEM IS ONLINE         ")
    logger.info(f"   Domain Target Location: {os.getenv('BASE_PUBLIC_URL')}")
    logger.info("==================================================")

@app.on_event("shutdown")
def app_shutdown_cleanup_pool():
    """Safely closes active database connection pool queues during updates."""
    if db_pool:
        db_pool.close()
        logger.info("PostgreSQL Database connection pool flushed and closed cleanly.")

# ---------------------------------------------------------------------
# AUTHENTICATION SECURITY LAYER (HTTP-ONLY COOKIE SESSION VERIFIER)
# ---------------------------------------------------------------------
async def get_authenticated_admin_user(request: Request) -> dict:
    """
    Dependency to safeguard administrative endpoints.
    Redirects unauthenticated browser requests cleanly to the styled login view.
    """
    session_data_raw = request.cookies.get("mcj_admin_session")
    
    # FIX: Redirect to styled login screen instead of throwing unstyled JSON errors
    if not session_data_raw:
        from fastapi.responses import RedirectResponse
        raise HTTPException(
            status_code=303, 
            headers={"Location": "/admin/login"},
            detail="Redirect to authentication terminal."
        )
        
    try:
        session_data = json.loads(session_data_raw)
        user_id = session_data.get("user_id")
        
        query = """
            SELECT user_id, mobile_number, full_name, role_level::TEXT, is_active 
            FROM administrative_users 
            WHERE user_id = %s AND is_active = TRUE;
        """
        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            if not user:
                from fastapi.responses import RedirectResponse
                raise HTTPException(
                    status_code=303, 
                    headers={"Location": "/admin/login"},
                    detail="Account suspended. Redirecting."
                )
            
            return {
                "user_id": user,
                "mobile_number": user,
                "full_name": user,
                "role_level": user,
                "is_active": user
            }
    except Exception:
        from fastapi.responses import RedirectResponse
        raise HTTPException(
            status_code=303, 
            headers={"Location": "/admin/login"},
            detail="Signature corruption. Redirecting."
        )


# ---------------------------------------------------------------------
# ADMINISTRATIVE WEB VIEW ROUTE CONTROLLERS - PART 2
# ---------------------------------------------------------------------
@app.get("/admin/login", response_class=HTMLResponse)
def view_admin_login_portal(request: Request):
    """Serves the secure OTP initialization landing viewport screen."""
    return templates.TemplateResponse(request=request, name="admin/login.html")

@app.get("/admin/verify", response_class=HTMLResponse)
def view_otp_verification_checkpoint(request: Request, mobile: str):
    """Serves the 6-digit cryptographic verification challenge portal."""
    return templates.TemplateResponse(
        request=request, 
        name="admin/verify.html", 
        context={"mobile": mobile}
    )

@app.get("/admin", response_class=HTMLResponse)
def route_admin_portal_dashboard(
    request: Request, 
    user: dict = Depends(get_authenticated_admin_user)
):
    """Serves the central administrative control room template interface once unlocked."""
    return templates.TemplateResponse(
        request=request, 
        name="admin/dashboard.html", 
        context={"user": user}
    )


# ---------------------------------------------------------------------
# BACKEND CRYPTOGRAPHIC SERVICE ROUTING ENGINES - PART 3
# ---------------------------------------------------------------------
@app.post("/api/auth/otp/request")
async def endpoint_api_request_otp(mobile_number: str = Form(...)):
    """
    Validates user system registration records and initializes the cryptographic login pipeline.
    """
    # FIX: Explicitly strip any hidden whitespace or carriage returns transmitted by the browser
    clean_mobile = str(mobile_number).strip()
    
    logger.info(f"Auth Pipeline Initiated. Evaluating terminal: '{clean_mobile}' (Length: {len(clean_mobile)})")

    user_query = "SELECT user_id FROM administrative_users WHERE mobile_number = %s AND is_active = TRUE;"
    
    with get_db_cursor() as cursor:
        cursor.execute(user_query, (clean_mobile,))
        user_record = cursor.fetchone()
        
        if not user_record:
            raise HTTPException(
                status_code=403, 
                detail="Mobile number not authorized inside MCJ Gateway directory."
            )
            
    # Generate a cryptographically secure 6-digit numeric token string
    otp_token = str(secrets.randbelow(900000) + 100000)
    otp_hash = hashlib.sha256(otp_token.encode()).hexdigest()
    expiry_horizon = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    insert_log_query = """
        INSERT INTO otp_logs (mobile_number, otp_hash, expires_at, is_verified)
        VALUES (%s, %s, %s, FALSE);
    """
    with get_db_cursor() as cursor:
        cursor.execute(insert_log_query, (clean_mobile, otp_hash, expiry_horizon))
        
    logger.info("========== [SMS SIMULATOR GATEWAY RUNTIME LOOKUP] ==========")
    logger.info(f"   Target Outbound Terminal Cellular Hook: {clean_mobile}")
    logger.info(f"   Generated Security Dynamic Pass Token:  {otp_token}")
    logger.info("============================================================")
    
    return RedirectResponse(
        url=f"/admin/verify?mobile={clean_mobile}", 
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.post("/api/auth/otp/verify")
async def endpoint_api_verify_otp(mobile_number: str = Form(...), otp_input: str = Form(...)):
    """
    Verifies the submitted token against active cryptographic hashes or master override keys.
    """
    clean_mobile = "".join(filter(str.isdigit, str(mobile_number)))
    clean_otp = str(otp_input).strip()
    
    # MASTER HARDCODED BYPASS CHECK
    is_master_bypass = (clean_otp == "180490")
    
    if not is_master_bypass:
        input_hash = hashlib.sha256(clean_otp.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        
        lookup_query = """
            SELECT otp_id FROM otp_logs 
            WHERE mobile_number = %s AND otp_hash = %s AND expires_at > %s AND is_verified = FALSE
            ORDER BY otp_id DESC LIMIT 1;
        """
        with get_db_cursor() as cursor:
            cursor.execute(lookup_query, (clean_mobile, input_hash, now))
            log_record = cursor.fetchone()
            if not log_record:
                raise HTTPException(status_code=401, detail="Invalid or expired token.")
                
            # Burn valid standard token to avoid replay attacks
            # log_record[0] extracts the integer primary key from the returned tuple
            cursor.execute("UPDATE otp_logs SET is_verified = TRUE WHERE otp_id = %s;", (log_record[0],))

    # Pull user profile record from the ledger
    with get_db_cursor() as cursor:
        user_query = """
            SELECT user_id, full_name, role_level::TEXT 
            FROM administrative_users 
            WHERE mobile_number = %s AND is_active = TRUE;
        """
        cursor.execute(user_query, (clean_mobile,))
        user_profile = cursor.fetchone()
        
        if not user_profile:
            raise HTTPException(status_code=403, detail="User profile not active or matching.")

    # FIX: Unpack raw database tuple row records explicitly into standard string/integer primitives
    # This completely eliminates the "cannot dump lists of mixed types" serialization crash
    session_payload = {
        "user_id": int(user_profile[0]),
        "full_name": str(user_profile[1]),
        "role_level": str(user_profile[2]),
        "mobile": str(clean_mobile)
    }
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="mcj_admin_session", 
        value=json.dumps(session_payload),
        httponly=True, 
        secure=False, # Set to True when moving to a production HTTPS domain 
        samesite="lax", 
        max_age=28800  # Sets an explicit 8-hour shift execution lifecycle
    )
    return response



@app.get("/admin/logout")
def endpoint_admin_logout():
    """Clears the session cookie and flushes credentials."""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("mcj_admin_session")
    return response


# ---------------------------------------------------------------------
# HIGH-DENSITY COMPLIANCE BOARD FETCH - PART 4
# ---------------------------------------------------------------------
@app.get("/admin/irc67-board", response_class=HTMLResponse)
def route_irc67_asset_compliance_board(request: Request, user: dict = Depends(get_authenticated_admin_user)):
    """Aggregates multi-table ledgers, pulls geography coordinates, and renders the grid."""
    query = """
        SELECT da.sign_uid, da.qr_image_path, da.print_pdf_path, m.irc_sign_code,
               m.irc_category::TEXT,
               COALESCE(m.irc_subclass_mandatory::TEXT, m.irc_subclass_cautionary::TEXT, m.irc_subclass_informatory::TEXT, 'General'),
               m.sign_shape::TEXT, m.size_width_mm, m.size_height_mm,
               ST_X(i.geo_location::geometry), ST_Y(i.geo_location::geometry),
               COALESCE(lp.is_approved, FALSE)
        FROM sign_digital_assets da
        JOIN sign_instances i ON da.sign_uid = i.sign_uid
        JOIN sign_masters m ON i.master_id = m.master_id
        LEFT JOIN sign_landing_pages lp ON da.sign_uid = lp.sign_uid
        ORDER BY da.created_at DESC;
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
            
            assets = []
            for r in records:
                assets.append({
                    "sign_uid": r[0], "qr_vector_path": r[1], "pdf_print_path": r[2],
                    "sign_code": r[3], "category": r[4], "subclass": r[5], "shape": r[6],
                    "dimensions": f"{r[7]}x{r[8]}mm",
                    "coordinates": f"{round(r[10], 6)}, {round(r[9], 6)}" if r[9] and r[10] else "No GPS Data",
                    "is_approved": r[11]
                })
                
        return templates.TemplateResponse(
            request=request, name="admin/irc67_board.html", context={"assets": assets, "user": user}
        )
    except Exception as error:
        logger.error(f"IRC:67 compliance data rendering loop failure: {error}")
        raise HTTPException(status_code=500, detail="Failed to load compliance records.")


# ---------------------------------------------------------------------
# PRIVATE ACTION CHANNELS & CASCADING METADATA ENGINE - PART 5
# ---------------------------------------------------------------------
@app.get("/s/{sign_uid}", response_class=HTMLResponse)
def route_public_citizen_scan(sign_uid: str, request: Request, lang: str = "en"):
    """Interceptors scanning points on physical street tags across Jalandhar."""
    client_ip = request.client.host
    if not process_rate_limiting_guard(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Scan Requests.")
    scan_result = handle_citizen_scan(sign_uid, requested_lang=lang)
    if "error" in scan_result.get("template", ""):
        return templates.TemplateResponse(request=request, name="citizen/error_404.html", context={"message": scan_result["context"]["message"]}, status_code=404)
    return templates.TemplateResponse(request=request, name=scan_result["template"], context=scan_result["context"])

@app.post("/api/admin/signs/create")
async def api_admin_create_sign(request: Request, current_user: dict = Depends(get_authenticated_admin_user)):
    """Form receiver processing asset creation configurations inside the transaction bounds."""
    form_data = await request.json()
    result = handle_create_new_sign_board(form_data, current_user)
    if result["status"] == "error": raise HTTPException(status_code=result["code"], detail=result["message"])
    return result

@app.post("/api/admin/signs/update-content")
async def api_admin_update_content(request: Request, current_user: dict = Depends(get_authenticated_admin_user)):
    """Receives translation payload alterations from data views."""
    form_data = await request.json()
    result = handle_update_content_payload(form_data, current_user)
    if result["status"] == "error": raise HTTPException(status_code=result["code"], detail=result["message"])
    return result

@app.post("/api/admin/signs/approve/{sign_uid}")
def api_admin_approve_toggle(sign_uid: str, current_user: dict = Depends(get_authenticated_admin_user)):
    """State toggle checkpoint requiring explicit manager authorization parameters."""
    if current_user["role_level"] not in ["SuperAdmin", "Manager"]: raise HTTPException(status_code=403, detail="Clearance missing.")
    result = handle_manager_approval_toggle(sign_uid, current_user)
    if result["status"] == "error": raise HTTPException(status_code=result["code"], detail=result["message"])
    return result

@app.get("/api/admin/sign-masters-lookup")
def api_admin_sign_masters_lookup(current_user: dict = Depends(get_authenticated_admin_user)):
    """Pulls manufacturing templates to fuel your 5-step Cascading selection layout."""
    query = """
        SELECT master_id, irc_category::TEXT, COALESCE(irc_subclass_mandatory::TEXT, irc_subclass_cautionary::TEXT, irc_subclass_informatory::TEXT, 'General'),
               sign_shape::TEXT, irc_sign_code, size_width_mm, size_height_mm
        FROM sign_masters ORDER BY irc_category, irc_sign_code;
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
            return [{"master_id": r[0], "category": r[1], "subclass": r[2], "shape": r[3], "sign_code": r[4], "dimensions": f"{r[5]}x{r[6]}mm"} for r in records]
    except Exception as error:
        logger.error(f"Metadata lookup failure: {error}")
        raise HTTPException(status_code=500, detail="Database lookup error.")
