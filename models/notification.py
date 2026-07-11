"""
Notification model – in-app notification CRUD.
"""
from database import fetch_one, fetch_all, execute


class Notification:
    """Manages user notifications."""

    @staticmethod
    def create(user_id, title, message, notif_type='info', incident_id=None):
        """Create a new notification."""
        return execute(
            """INSERT INTO notifications (user_id, title, message, type, incident_id)
               VALUES (%s, %s, %s, %s, %s)""",
            (user_id, title, message, notif_type, incident_id)
        )

    @staticmethod
    def get_for_user(user_id, limit=20, unread_only=False):
        """Get notifications for a user, newest first."""
        if unread_only:
            return fetch_all(
                """SELECT * FROM notifications
                   WHERE user_id = %s AND is_read = 0
                   ORDER BY created_at DESC LIMIT %s""",
                (user_id, limit)
            )
        return fetch_all(
            """SELECT * FROM notifications
               WHERE user_id = %s
               ORDER BY created_at DESC LIMIT %s""",
            (user_id, limit)
        )

    @staticmethod
    def count_unread(user_id):
        row = fetch_one(
            "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = %s AND is_read = 0",
            (user_id,)
        )
        return row['cnt'] if row else 0

    @staticmethod
    def mark_read(notification_id):
        execute(
            "UPDATE notifications SET is_read = 1 WHERE id = %s",
            (notification_id,)
        )

    @staticmethod
    def mark_all_read(user_id):
        execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = %s",
            (user_id,)
        )

    @staticmethod
    def delete(notification_id):
        execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
