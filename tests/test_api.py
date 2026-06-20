"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Automated Suite: Administrative API Endpoint Authorization & Sanitization Tests
"""

from src.web.admin_handlers import handle_manager_approval_toggle, handle_update_content_payload
from src.web.middleware import sanitize_input_text

def test_four_eyes_principle_role_enforcement():
    """
    Asserts that a data entry 'Creator' cannot self-approve content.
    The system must explicitly return an error status code to enforce compliance.
    """
    mock_creator_session = {
        "user_id": 42,
        "role_level": "Creator",  # Creator accounts lack permission to authorize data visibility live
        "is_active": True
    }
    
    # Simulate a Creator trying to bypass controls on an unapproved road sign board tracking token
    target_sign_uid = "MCJ-POST-WZ1-0024-X7R2"
    result = handle_manager_approval_toggle(target_sign_uid, mock_creator_session)
    
    assert result["status"] == "error", "Security Policy Violation: Creator account bypass detected!"
    assert result["code"] == 403, "Authorization Failure: Expected HTTP 403 Forbidden status descriptor."

def test_xss_input_sanitization_filter():
    """
    Verifies that malicious Cross-Site Scripting (XSS) HTML/JS injection payloads 
    inside trilingual forms are neutralized before database mutation operations.
    """
    dangerous_punjabi_payload = "<script>alert('hacked')</script> ਸ਼ਹੀਦ ਭਗਤ ਸਿੰਘ ਮੈਮੋਰੀਅਲ"
    sanitized_output = sanitize_input_text(dangerous_punjabi_payload)
    
    # Malicious bracket identifiers must be safely escaped into standard entity text characters
    assert "<script>" not in sanitized_output, "Sanitization Security Defect: Raw executable code injection slipped through!"
    assert "&lt;script&gt;" in sanitized_output, "Sanitization Success: Code fragments successfully escaped."
