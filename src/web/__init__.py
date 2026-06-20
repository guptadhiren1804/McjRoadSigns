"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Web Handling and Routing Package Initializer
"""

from src.web.public_handlers import handle_citizen_scan
from src.web.admin_handlers import (
    handle_create_new_sign_board,
    handle_update_content_payload,
    handle_manager_approval_toggle
)
from src.web.middleware import (
    sanitize_input_text,
    process_rate_limiting_guard,
    enforce_admin_session_guard
)

# Export verified routing systems and security filters to main.py
__all__ = [
    "handle_citizen_scan",
    "handle_create_new_sign_board",
    "handle_update_content_payload",
    "handle_manager_approval_toggle",
    "sanitize_input_text",
    "process_rate_limiting_guard",
    "enforce_admin_session_guard"
]
