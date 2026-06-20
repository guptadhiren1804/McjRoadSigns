"""
Municipal Corporation Jalandhar Road Signs Project (McjRoadSigns)
Data Model: Operational Change and Audit Logs Tracking
"""

import json
import logging
from config.database import get_db_cursor

logger = logging.getLogger("McjRoadSigns.Models.Audit")

class AuditModel:
    @staticmethod
    def log_operational_action(target_table: str, record_id: int, user_id: int, action_performed: str, old_value: dict or None, new_value: dict or None, ip_address: str) -> bool:
        """
        Records data modifications directly into the system audit ledger.
        Saves snapshot histories using JSON strings to verify change metrics.
        """
        query = """
            INSERT INTO operational_audit_logs (target_table, record_id, user_id, action_performed, old_value_json, new_value_json, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        
        # Convert dictionary inputs to clean JSON strings for database compatibility
        old_json_str = json.dumps(old_value) if old_value else None
        new_json_str = json.dumps(new_value) if new_value else None

        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (
                    target_table.strip(),
                    record_id,
                    user_id,
                    action_performed.strip().upper(),  # 'INSERT', 'UPDATE', or 'DELETE'
                    old_json_str,
                    new_json_str,
                    ip_address.strip()
                ))
            return True
        except Exception as error:
            logger.error(f"Failed to record footprint transaction inside audit trail: {error}")
            return False
