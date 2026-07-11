"""
Shared helper functions – pagination, file validation, date formatting, audit logging.
"""
import math
import re
from datetime import datetime
from database import execute
from flask import request


def paginate(total, page, per_page):
    """
    Return a pagination dict for use in templates.
    """
    total_pages = max(1, math.ceil(total / per_page))
    page = max(1, min(page, total_pages))
    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None,
        'pages': list(range(max(1, page - 2), min(total_pages + 1, page + 3)))
    }


def format_datetime(dt, fmt='%d %b %Y, %I:%M %p'):
    """Format a datetime object to a human-readable string."""
    if isinstance(dt, str):
        try:
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return dt
    if dt:
        return dt.strftime(fmt)
    return ''


def format_file_size(size_bytes):
    """Convert bytes to a human-readable size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def validate_email(email):
    """Basic email format validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Basic phone number validation (allows digits, spaces, +, -)."""
    if not phone:
        return True
    pattern = r'^[\d\s\+\-\(\)]{7,20}$'
    return re.match(pattern, phone) is not None


def validate_password(password):
    """
    Enforce minimum password strength:
    - At least 8 characters
    - At least one uppercase letter
    - At least one digit
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    return True, ""


def sanitize_input(text):
    """Strip dangerous HTML but allow basic text."""
    if text is None:
        return None
    import bleach
    return bleach.clean(str(text).strip())


def log_audit(user_id, action, details=None):
    """Record an action in the audit log."""
    ip = request.remote_addr if request else None
    execute(
        """INSERT INTO audit_logs (user_id, action, details, ip_address)
           VALUES (%s, %s, %s, %s)""",
        (user_id, action, details, ip)
    )


def get_status_percentage(status):
    """Return a percentage for the progress bar based on status."""
    mapping = {
        'Pending': 10,
        'Assigned': 30,
        'Under Investigation': 60,
        'Resolved': 90,
        'Closed': 100
    }
    return mapping.get(status, 0)


def get_status_color(status):
    """Return a Bootstrap color class for a status value."""
    mapping = {
        'Pending': 'warning',
        'Assigned': 'info',
        'Under Investigation': 'primary',
        'Resolved': 'success',
        'Closed': 'secondary'
    }
    return mapping.get(status, 'secondary')


def get_priority_color(priority):
    """Return a Bootstrap color class for a priority value."""
    mapping = {
        'low': 'success',
        'medium': 'info',
        'high': 'warning',
        'critical': 'danger'
    }
    return mapping.get(priority, 'secondary')
