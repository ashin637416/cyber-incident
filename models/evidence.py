"""
Evidence model – manages file uploads, metadata, and audit trails.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from database import fetch_one, fetch_all, execute
from config import Config


class Evidence:
    """Handles evidence file storage and metadata."""

    @staticmethod
    def get_upload_subfolder(extension):
        """Determine the subfolder based on file extension."""
        ext = extension.lower()
        if ext in Config.ALLOWED_IMAGE_EXTENSIONS:
            return 'images'
        elif ext in Config.ALLOWED_VIDEO_EXTENSIONS:
            return 'videos'
        else:
            return 'documents'

    @staticmethod
    def generate_unique_filename(original_filename):
        """Create a UUID-prefixed filename to avoid collisions."""
        name = secure_filename(original_filename)
        ext = name.rsplit('.', 1)[-1] if '.' in name else ''
        unique_name = f"{uuid.uuid4().hex}_{name}"
        return unique_name, ext

    @staticmethod
    def save_file(file, incident_id, uploaded_by):
        """
        Validate, save a file to disk, and record metadata in the DB.
        Returns the new evidence id or raises ValueError on failure.
        """
        if not file or file.filename == '':
            raise ValueError("No file selected.")

        original_name = file.filename
        unique_name, ext = Evidence.generate_unique_filename(original_name)

        if ext.lower() not in Config().ALLOWED_EXTENSIONS:
            raise ValueError(f"File type '.{ext}' is not allowed.")

        subfolder = Evidence.get_upload_subfolder(ext)
        folder_path = os.path.join(Config.UPLOAD_FOLDER, subfolder)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, unique_name)
        file.save(file_path)

        # Determine file size
        file_size = os.path.getsize(file_path)

        # Determine file type category
        file_type = subfolder.rstrip('s')  # 'image', 'document', 'video'

        # Store relative path for portability
        relative_path = os.path.join('uploads', subfolder, unique_name)

        evidence_id = execute(
            """INSERT INTO evidence
                (incident_id, file_name, original_name, file_path,
                 file_type, file_size, uploaded_by)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (incident_id, unique_name, original_name, relative_path,
             file_type, file_size, uploaded_by)
        )
        return evidence_id

    # ── Read ───────────────────────────────────────────────────────
    @staticmethod
    def get_by_id(evidence_id):
        return fetch_one("SELECT * FROM evidence WHERE id = %s", (evidence_id,))

    @staticmethod
    def get_by_incident(incident_id):
        return fetch_all(
            """SELECT e.*, u.full_name AS uploader_name
               FROM evidence e
               JOIN users u ON e.uploaded_by = u.id
               WHERE e.incident_id = %s
               ORDER BY e.created_at DESC""",
            (incident_id,)
        )

    # ── Update ─────────────────────────────────────────────────────
    @staticmethod
    def update_notes(evidence_id, notes):
        execute(
            "UPDATE evidence SET notes = %s WHERE id = %s",
            (notes, evidence_id)
        )

    # ── Delete ─────────────────────────────────────────────────────
    @staticmethod
    def delete(evidence_id):
        """Delete evidence record and the physical file."""
        ev = Evidence.get_by_id(evidence_id)
        if ev:
            # Try to remove the physical file
            full_path = os.path.join(
                os.path.dirname(Config.UPLOAD_FOLDER),
                ev['file_path']
            )
            if os.path.exists(full_path):
                os.remove(full_path)
            execute("DELETE FROM evidence WHERE id = %s", (evidence_id,))
            return True
        return False
