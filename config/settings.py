"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Global Settings Mapping Module (With Native .env Parser)
"""

import os
from pathlib import Path

# Base Project Directory Resolver
BASE_DIR = Path(__file__).resolve().parent.parent

# --- NATIVE .ENV LOADER WORKAROUND ---
# Since we are running locally without Docker or third-party dotenv wrappers,
# this code reads the text file directly and injects it into Python's memory.
env_file_path = BASE_DIR / ".env"
if env_file_path.exists():
    with open(env_file_path, "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            # Skip empty lines or comment lines
            if not clean_line or clean_line.startswith("#"):
                continue
            if "=" in clean_line:
                key, val = clean_line.split("=", 1)
                os.environ[key.strip()] = val.strip()
# -------------------------------------

# Application Core Runtime Mappings
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")

# Real purchased domain name asset parameter location
BASE_PUBLIC_URL = os.getenv("BASE_PUBLIC_URL", "https://mcjroadsigns.in").rstrip("/")

# Enterprise Telecom SMS Key Indicators
SMS_GATEWAY_PROVIDER = os.getenv("SMS_GATEWAY_PROVIDER", "development").lower()
SMS_API_KEY = os.getenv("SMS_API_KEY")
SMS_SENDER_ID = os.getenv("SMS_SENDER_ID", "MCJMUN")

try:
    OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 3))
except (ValueError, TypeError):
    OTP_EXPIRY_MINUTES = 3

# Storage Vault Configurations
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
STORAGE_BASE_PATH = os.getenv("STORAGE_BASE_PATH", str(BASE_DIR / "storage"))

try:
    MEDIA_MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MEDIA_MAX_UPLOAD_SIZE_BYTES", 5242880)) # Default 5MB
except (ValueError, TypeError):
    MEDIA_MAX_UPLOAD_SIZE_BYTES = 5242880

# Security Parameter Assertions Guard Check
if not APP_SECRET_KEY or "generate_and_paste" in APP_SECRET_KEY:
    import sys
    print("CRITICAL SECURITY ERROR: APP_SECRET_KEY is insecure or missing inside .env configurations!")
    sys.exit(1)
