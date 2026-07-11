"""
User model – handles authentication, profile management, and role checking.
Implements Flask-Login's UserMixin for session integration.
"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import fetch_one, fetch_all, execute, execute_with_rowcount


class User(UserMixin):
    """Represents a portal user (citizen, officer, or admin)."""

    def __init__(self, user_data: dict):
        self.id = user_data['id']
        self.full_name = user_data['full_name']
        self.email = user_data['email']
        self.phone = user_data.get('phone')
        self.role = user_data['role']
        self.address = user_data.get('address')
        self.is_active_flag = user_data.get('is_active', 1)
        self.avatar = user_data.get('avatar')
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')

    # ── Flask-Login helpers ────────────────────────────────────────
    @property
    def is_active(self):
        return bool(self.is_active_flag)

    def is_admin(self):
        return self.role == 'admin'

    def is_officer(self):
        return self.role == 'officer'

    def is_citizen(self):
        return self.role == 'citizen'

    # ── Class Methods (CRUD) ───────────────────────────────────────
    @staticmethod
    def get_by_id(user_id):
        """Load user by primary key."""
        row = fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))
        return User(row) if row else None

    @staticmethod
    def get_by_email(email):
        """Load user by email address."""
        row = fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        return User(row) if row else None

    @staticmethod
    def create(full_name, email, phone, password, role='citizen'):
        """Register a new user. Returns the new user's id."""
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        return execute(
            """INSERT INTO users (full_name, email, phone, password_hash, role)
               VALUES (%s, %s, %s, %s, %s)""",
            (full_name, email, phone, password_hash, role)
        )

    @staticmethod
    def verify_password(email, password):
        """Return User object if credentials are valid, else None."""
        row = fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        if row and check_password_hash(row['password_hash'], password):
            return User(row)
        return None

    @staticmethod
    def update_profile(user_id, full_name, phone, address):
        """Update basic profile fields."""
        execute(
            """UPDATE users SET full_name = %s, phone = %s, address = %s
               WHERE id = %s""",
            (full_name, phone, address, user_id)
        )

    @staticmethod
    def change_password(user_id, new_password):
        """Set a new password hash."""
        password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, user_id)
        )

    @staticmethod
    def check_current_password(user_id, password):
        """Verify the user's current password."""
        row = fetch_one("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        if row:
            return check_password_hash(row['password_hash'], password)
        return False

    @staticmethod
    def get_all(role=None, page=1, per_page=10, search=None):
        """Return paginated user list with optional role and search filter."""
        offset = (page - 1) * per_page
        conditions = []
        params = []

        if role:
            conditions.append("role = %s")
            params.append(role)
        if search:
            conditions.append("(full_name LIKE %s OR email LIKE %s)")
            params.extend([f'%{search}%', f'%{search}%'])

        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        total = fetch_one(f"SELECT COUNT(*) AS cnt FROM users{where}", params)['cnt']
        params.extend([per_page, offset])
        rows = fetch_all(
            f"SELECT * FROM users{where} ORDER BY created_at DESC LIMIT %s OFFSET %s",
            params
        )
        return rows, total

    @staticmethod
    def toggle_active(user_id):
        """Toggle a user's is_active flag."""
        execute(
            "UPDATE users SET is_active = NOT is_active WHERE id = %s",
            (user_id,)
        )

    @staticmethod
    def count_by_role(role=None):
        """Count users, optionally filtered by role."""
        if role:
            row = fetch_one("SELECT COUNT(*) AS cnt FROM users WHERE role = %s", (role,))
        else:
            row = fetch_one("SELECT COUNT(*) AS cnt FROM users")
        return row['cnt'] if row else 0
