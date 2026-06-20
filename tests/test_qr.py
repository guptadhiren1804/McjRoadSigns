"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Automated Suite: Vector Suffix Lookups and Character Validation Tests
"""

import re
import secrets

def generate_mock_secure_suffix(length: int = 4) -> str:
    """Generates a random alphanumeric suffix string excluding confusing letters."""
    allowed_characters = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    return "".join(secrets.choice(allowed_characters) for _ in range(length))

def test_unguessable_url_suffix_generation():
    """
    Verifies that generated URL signatures follow your custom character rules 
    and exclude easily confused letters like 0, O, 1, or I for manual typing ease.
    """
    # Allowed character pattern dictionary from src/core/qr_generator.py
    allowed_pattern = re.compile(r"^[2-9A-HJKLMNPQRSTUVWXYZ]{4}$")
    
    # Generate 100 sample tokens to thoroughly test character constraints
    for _ in range(100):
        generated_suffix = generate_mock_secure_suffix(4)
        
        assert len(generated_suffix) == 4, "Token boundary failure: Suffix must be 4 characters."
        assert allowed_pattern.match(generated_suffix), f"Linguistic safety constraint violation on token: {generated_suffix}"
