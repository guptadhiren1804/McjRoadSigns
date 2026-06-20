"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Web Security Layer: Rate Limiting, Input Sanitization, and Session Guards
"""

import time
import logging
import html

logger = logging.getLogger("McjRoadSigns.Web.Middleware")

# In-memory rate-limiter ledger (For multi-server scale, this maps to a Redis instance)
ip_request_history = {}
PUBLIC_RATE_LIMIT_PER_MINUTE = 60

def sanitize_input_text(raw_text: str) -> str:
    """
    Strips dangerous characters and escapes HTML inputs.
    Prevents Cross-Site Scripting (XSS) inside trilingual content fields.
    """
    if not raw_text:
        return ""
    # Strip whitespace buffers and escape structural character sequences safely
    return html.escape(raw_text.strip())

def process_rate_limiting_guard(client_ip: str) -> bool:
    """
    Protects public scan routes against automated scraping scripts.
    Blocks the request if an IP address exceeds 60 requests per minute.
    """
    current_timestamp = time.time()
    
    if client_ip not in ip_request_history:
        ip_request_history[client_ip] = []
        
    # Flush log entry history objects older than 60 seconds
    ip_request_history[client_ip] = [
        ts for ts in ip_request_history[client_ip] if current_timestamp - ts < 60
    ]
    
    # Check threshold bounds violations
    if len(ip_request_history[client_ip]) >= PUBLIC_RATE_LIMIT_PER_MINUTE:
        logger.warning(f"SECURITY THREAT SUSPECTED: Rate limit threshold broken by IP: {client_ip}")
        return False
        
    ip_request_history[client_ip].append(current_timestamp)
    return True

# src/web/middleware.py

def enforce_admin_session_guard(session_user) -> bool:
    """
    Validates administrative operational credentials.
    Adapts gracefully to both database tuple lookups and standard user dictionaries.
    Authorized Tiers: SuperAdmin, Manager, Creator
    """
    if not session_user:
        return False

    # Scenario A: Middleware receives a database query row context tuple
    # Structure: (5, '9041207675', 'Dhiren Gupta', 'SuperAdmin', True)
    if isinstance(session_user, (tuple, list)):
        try:
            role = session_user[3]
            is_active = session_user[4] if len(session_user) > 4 else True
            
            # Match the target corporate administrative matrix exactly
            if is_active and role in ["SuperAdmin", "Manager", "Creator"]:
                return True
        except IndexError:
            return False

    # Scenario B: Middleware receives a raw session dictionary format
    elif isinstance(session_user, dict):
        role = session_user.get("role_level")
        is_active = session_user.get("is_active", True)
        
        if is_active and role in ["SuperAdmin", "Manager", "Creator"]:
            return True

    return False

