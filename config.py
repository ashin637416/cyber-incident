"""
Configuration settings for the Cyber Incident Reporting Portal.
Update MySQL credentials and SECRET_KEY for your environment.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    # ── Secret Key (CHANGE IN PRODUCTION) ──────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cyber-incident-portal-secret-key-change-me')

    # ── SQLite Database ─────────────────────────────────────────────────
    DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'cyber_incident_portal.db'))


    # ── Session Configuration ──────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # ── File Upload Configuration ──────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'webm'}

    @property
    def ALLOWED_EXTENSIONS(self):
        return (
            self.ALLOWED_IMAGE_EXTENSIONS
            | self.ALLOWED_DOCUMENT_EXTENSIONS
            | self.ALLOWED_VIDEO_EXTENSIONS
        )

    # ── Report Output Directory ────────────────────────────────────────
    REPORTS_FOLDER = os.path.join(BASE_DIR, 'reports')

    # ── Pagination ─────────────────────────────────────────────────────
    ITEMS_PER_PAGE = 10

    # ── Incident Case ID Prefix ────────────────────────────────────────
    CASE_ID_PREFIX = 'CIR'
