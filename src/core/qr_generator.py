"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Core Asset Engine: Fast Random Token sign_uid and QR Compiler Layer
"""

import os
import secrets
import logging
import segno

logger = logging.getLogger("McjRoadSigns.QRGenerator")

BASE_PUBLIC_URL = os.getenv("BASE_PUBLIC_URL")
STORAGE_BASE_PATH = os.getenv("STORAGE_BASE_PATH", "./storage")

def generate_random_uid(length: int = 10) -> str:
    """
    Generates a cryptographically secure, random alphanumeric token.
    Excludes look-alike characters (0, O, 1, I) to ensure manual typing remains effortless.
    """
    allowed_characters = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    return "".join(secrets.choice(allowed_characters) for _ in range(length))

def generate_sign_qr_asset(cursor) -> dict:
    """
    1. Generates a fast, secure 10-character alphanumeric sign_uid.
    2. Renders a microscopic high-contrast Level-H vector QR asset file.
    3. Commits the path layout records directly into the file ledger.
    """
    if not BASE_PUBLIC_URL:
        raise ValueError("CRITICAL CONFIGURATION ERROR: BASE_PUBLIC_URL environment variable is missing!")

    # 1. Generate the completely random key
    sign_uid = generate_random_uid(10) # e.g., 'X7R2K9P4M3'

    # 2. Setup standard URL and system disk paths
    short_routing_url = f"{BASE_PUBLIC_URL.rstrip('/')}/s/{sign_uid}"
    qr_filename = f"{sign_uid}.svg"
    pdf_filename = f"{sign_uid}.pdf"
    
    qr_relative_path = f"qr_vectors/{qr_filename}"
    pdf_relative_path = f"sign_pdfs/{pdf_filename}"
    
    qr_absolute_path = os.path.join(STORAGE_BASE_PATH, qr_relative_path)
    pdf_absolute_path = os.path.join(STORAGE_BASE_PATH, pdf_relative_path)

    os.makedirs(os.path.dirname(qr_absolute_path), exist_ok=True)
    os.makedirs(os.path.dirname(pdf_absolute_path), exist_ok=True)

    # 3. Compile Vector QR code graphic (Level H = 30% street damage proof)
    qr_code = segno.make_qr(short_routing_url, error='H')
    qr_code.save(qr_absolute_path, kind='svg', scale=10, dark='#0F172A', light='#FFFFFF')
    
    # 4. Commit paths to the isolated file ledger table
    insert_asset_query = """
        INSERT INTO sign_digital_assets (sign_uid, short_routing_url, qr_image_path, print_pdf_path)
        VALUES (%s, %s, %s, %s);
    """
    cursor.execute(insert_asset_query, (sign_uid, short_routing_url, qr_relative_path, pdf_relative_path))
    
    logger.info(f"Fast random tracking key compiled successfully: {sign_uid}")
    
    return {
        "sign_uid": sign_uid,
        "qr_svg_absolute_path": qr_absolute_path,
        "pdf_absolute_path": pdf_absolute_path
    }
