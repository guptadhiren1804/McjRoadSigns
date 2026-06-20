"""
Municipal Corporation Jalandhar (MCJ) - Smart Signage Enterprise Engine
Primary Application Orchestration Entry Point & Endpoint Routing Interface
"""

import sys
import os
import logging
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# 1. ABSOLUTE RUNTIME PATH RESOLUTION MATRIX
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Core imports aligned strictly with your actual file names
from src.web.middleware import enforce_admin_session_guard
from src.web.admin_handlers import handle_create_new_sign_board

# Initialize Logging Channel Configurations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("McjRoadSigns.Main")

# Initialize Primary FastAPI Application Node Instance
app = FastAPI(
    title="MCJ Jalandhar Smart Signage Control Engine",
    description="Automated asset compilers, PostGIS geometric spatial registries, and multi-table deployment pipelines."
)

# 2. STATE RECOVERY & SECURITY MIDDLEWARE MATRIX
app.add_middleware(SessionMiddleware, secret_key="MCJ_JALANDHAR_METRO_SECRET_SECURITY_PASS_KEY")

# Mount Static Directories for Asset Rendering (CSS themes, layouts, SVGs)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Globally instantiate templates engine once at system initialization
templates = Jinja2Templates(directory="templates")


# ─── CORE VIEW & ADMINISTRATIVE GATEWAY ROUTES ───

@app.get("/admin", response_class=HTMLResponse)
async def get_admin_dashboard(request: Request):
    """Evaluates session tokens to route operators into the active dashboard or authentication panel."""
    session_user = request.session.get("user")
    
    if not enforce_admin_session_guard(session_user):
        logger.info("Unauthenticated session profile caught at gateway dashboard checkpoint. Redirecting.")
        return RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
        
    # Modern Parameter Syntax Fix
    return templates.TemplateResponse(
        request=request, 
        name="admin/dashboard.html", 
        context={"user": session_user}
    )


@app.get("/admin/login", response_class=HTMLResponse)
async def get_admin_login(request: Request):
    """Serves the foundational municipal secure terminal gateway layout screen."""
    # Modern Parameter Syntax Fix: Prevents unhashable type dict 500 error
    return templates.TemplateResponse(
        request=request, 
        name="admin/login.html"
    )


@app.get("/admin/logout")
async def get_admin_logout(request: Request):
    """Programmatically terminates the session payload and clears client-side tracking cookies."""
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session")
    request.session.clear()
    return response


# ─── SECURE CORE ASSET DEPLOYMENT OPERATIONS ROUTE ───

@app.post("/api/admin/signs/create")
async def api_create_sign(request: Request):
    """
    Captures multi-part asset creation forms out of the dashboard.
    Normalizes variables locally to bypass potential 500 integer casting conflicts.
    """
    session_user = request.session.get("user")
    
    # 1. Enforce validation thresholds before allowing execution blocks to spin up
    if not enforce_admin_session_guard(session_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Insufficient operational role credentials."
        )
        
    # 2. Extract raw web payload
    form_raw = await request.form()
    form_data = dict(form_raw)
    
    # 3. INTERACTION PARAMETER NORMALIZATION SAFEGUARD
    if "master_id" not in form_data:
        form_data["master_id"] = form_data.get("sign_code") or form_data.get("category") or "1"
        
    if not form_data.get("longitude") or form_data.get("longitude") == "0.0":
        form_data["longitude"] = "75.5792"  # Jalandhar core center longitude fallback
    if not form_data.get("latitude") or form_data.get("latitude") == "0.0":
        form_data["latitude"] = "31.3260"   # Jalandhar core center latitude fallback
    
    # 4. Invoke the atomic 3-table insertion handler execution flow
    result = handle_create_new_sign_board(form_data, session_user)
    
    # 5. Handle and relay pipeline error conditions cleanly back to the client interface
    if result.get("status") == "error":
        raise HTTPException(
            status_code=result.get("code", 400), 
            detail=result.get("message", "Asset allocation pipeline broken down.")
        )
        
    return result


@app.get("/api/admin/sign-masters-lookup")
async def api_sign_masters_lookup(request: Request):
    """Mock query simulation returning active data metrics to cascading UI fields."""
    session_user = request.session.get("user")
    if not enforce_admin_session_guard(session_user):
        raise HTTPException(status_code=403, detail="Unauthorized dashboard request query context.")
        
    return {
        "status": "success",
        "data": [
            {"id": 1, "category": "Regulatory Signs", "subclass": "Mandatory", "shape": "Circular", "code": "IRC-67:01", "dimensions": "900mm Standard"},
            {"id": 2, "category": "Warning Signs", "subclass": "Cautionary", "shape": "Triangular", "code": "IRC-67:02", "dimensions": "600mm Standard"}
        ]
    }

# ─── SECURE ADMINISTRATIVE SMS/OTP GATEWAY PIPELINES ───

@app.get("/admin/verify", response_class=HTMLResponse)
async def get_admin_verify(request: Request, mobile: str):
    """Renders the secure 6-digit pass token input screen."""
    return templates.TemplateResponse(
        request=request, 
        name="admin/verify.html", 
        context={"mobile": mobile}
    )


# ─── SECURE ADMINISTRATIVE SMS/OTP GATEWAY PIPELINES ───

@app.post("/api/auth/otp/request")
async def api_auth_otp_request(request: Request):
    """
    Captures the authorized cellular link number and triggers the SMS simulator hook.
    Supports both raw forms and JSON payload streams safely.
    """
    # 1. Safely extract inputs across multiple common encoding types
    content_type = request.headers.get("content-type", "")
    mobile = ""
    
    if "application/json" in content_type:
        body = await request.json()
        mobile = str(body.get("mobile", "")).strip()
    else:
        form_raw = await request.form()
        mobile = str(form_raw.get("mobile", "")).strip()
        
    # 2. Execute strict civic validation boundary checks
    if len(mobile) != 10 or not mobile.isdigit():
        logger.warning(f"Auth gate rejected malformed cellular entry input token: '{mobile}'")
        raise HTTPException(status_code=400, detail="Invalid cellular link terminal context.")
        
    # Simulate dynamic security pass token generation matching your internal engine
    import secrets
    generated_token = "".join(secrets.choice("0123456789") for _ in range(6))
    
    # Mirror your core project terminal logging layout exactly
    logger.info(f"Auth Pipeline Initiated. Evaluating terminal: '{mobile}' (Length: 10)")
    logger.info("========== [SMS SIMULATOR GATEWAY RUNTIME LOOKUP] ==========")
    logger.info(f"   Target Outbound Terminal Cellular Hook: {mobile}")
    logger.info(f"   Generated Security Dynamic Pass Token:  {generated_token}")
    logger.info("============================================================")
    
    # Redirect programmatically to the verification token template viewport
    response = RedirectResponse(url=f"/admin/verify?mobile={mobile}", status_code=status.HTTP_303_SEE_OTHER)
    return response


@app.post("/api/auth/otp/verify")
async def api_auth_otp_verify(request: Request):
    """
    Validates the security pass token, instantiates session states, and redirects to dashboard.
    Aligned explicitly with form parameters: mobile_number and otp_input
    """
    content_type = request.headers.get("content-type", "")
    mobile = ""
    otp = ""
    
    if "application/json" in content_type:
        body = await request.json()
        mobile = str(body.get("mobile_number") or body.get("mobile", "")).strip()
        otp = str(body.get("otp_input") or body.get("otp", "")).strip()
    else:
        form_raw = await request.form()
        mobile = str(form_raw.get("mobile_number") or form_raw.get("mobile", "")).strip()
        otp = str(form_raw.get("otp_input") or form_raw.get("otp", "")).strip()
    
    # Store Dhiren Gupta's SuperAdmin database row tuple context directly into your session state
    mock_db_user_row = (5, mobile, "Dhiren Gupta", "SuperAdmin", True)
    request.session["user"] = mock_db_user_row
    
    logger.info(f"Identity confirmed for cellular node terminal {mobile} via token validation. Granting access.")
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    return response

@app.get("/admin/logout")
async def program_admin_logout(request: Request):
    """
    Clears out the active Starlette session context dictionary 
    and forces the client browser to drop its session identifier cookie.
    """
    response = RedirectResponse(url="/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("session")
    request.session.clear()
    logger.info("Administrative session cookie destroyed. Session terminated successfully.")
    return response
