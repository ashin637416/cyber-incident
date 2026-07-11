"""
Incident model – case ID generation, CRUD, search / filter / pagination,
status workflow, and officer assignment.
"""
from datetime import datetime
from database import fetch_one, fetch_all, execute


class Incident:
    """Represents a cyber incident report."""

    # Valid status transitions
    STATUS_FLOW = {
        'Pending': ['Assigned'],
        'Assigned': ['Under Investigation'],
        'Under Investigation': ['Resolved'],
        'Resolved': ['Closed'],
        'Closed': []
    }

    STATUS_LIST = ['Pending', 'Assigned', 'Under Investigation', 'Resolved', 'Closed']

    PRIORITY_LIST = ['low', 'medium', 'high', 'critical']

    # ── Case ID Generation ─────────────────────────────────────────
    @staticmethod
    def generate_case_id():
        """
        Generate a unique Case ID in the format CIR + YYYY + 5-digit sequence.
        Example: CIR202600001
        """
        year = datetime.now().strftime('%Y')
        prefix = f'CIR{year}'
        row = fetch_one(
            "SELECT case_id FROM incidents WHERE case_id LIKE %s ORDER BY id DESC LIMIT 1",
            (f'{prefix}%',)
        )
        if row:
            last_seq = int(row['case_id'][len(prefix):])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        return f'{prefix}{new_seq:05d}'

    # ── Create ─────────────────────────────────────────────────────
    @staticmethod
    def create(data: dict):
        """
        Insert a new incident. `data` must contain all required fields.
        Returns the new incident id.
        """
        case_id = Incident.generate_case_id()
        return execute(
            """INSERT INTO incidents
                (case_id, user_id, category_id, title, incident_type, description,
                 incident_date, incident_time, location, website_involved,
                 email_involved, phone_involved, social_media, financial_loss,
                 additional_comments, priority)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                case_id,
                data['user_id'],
                data.get('category_id'),
                data['title'],
                data['incident_type'],
                data['description'],
                data['incident_date'],
                data.get('incident_time'),
                data.get('location'),
                data.get('website_involved'),
                data.get('email_involved'),
                data.get('phone_involved'),
                data.get('social_media'),
                data.get('financial_loss', 0),
                data.get('additional_comments'),
                data.get('priority', 'medium'),
            )
        )

    # ── Read ───────────────────────────────────────────────────────
    @staticmethod
    def get_by_id(incident_id):
        """Get a single incident by primary key with officer & user info."""
        return fetch_one(
            """SELECT i.*,
                      u.full_name AS reporter_name, u.email AS reporter_email,
                      o.full_name AS officer_name,
                      ic.name     AS category_name
               FROM incidents i
               JOIN users u ON i.user_id = u.id
               LEFT JOIN users o ON i.assigned_officer_id = o.id
               LEFT JOIN incident_categories ic ON i.category_id = ic.id
               WHERE i.id = %s""",
            (incident_id,)
        )

    @staticmethod
    def get_by_case_id(case_id):
        """Look up by the human-readable case ID string."""
        return fetch_one(
            """SELECT i.*,
                      u.full_name AS reporter_name, u.email AS reporter_email,
                      o.full_name AS officer_name,
                      ic.name     AS category_name
               FROM incidents i
               JOIN users u ON i.user_id = u.id
               LEFT JOIN users o ON i.assigned_officer_id = o.id
               LEFT JOIN incident_categories ic ON i.category_id = ic.id
               WHERE i.case_id = %s""",
            (case_id,)
        )

    # ── List with filters ─────────────────────────────────────────
    @staticmethod
    def get_all(page=1, per_page=10, user_id=None, officer_id=None,
                status=None, priority=None, search=None, sort_by='created_at',
                sort_dir='DESC'):
        """Paginated, filtered, sortable incident list."""
        conditions = []
        params = []

        if user_id:
            conditions.append("i.user_id = %s")
            params.append(user_id)
        if officer_id:
            conditions.append("i.assigned_officer_id = %s")
            params.append(officer_id)
        if status:
            conditions.append("i.status = %s")
            params.append(status)
        if priority:
            conditions.append("i.priority = %s")
            params.append(priority)
        if search:
            conditions.append(
                "(i.case_id LIKE %s OR i.title LIKE %s OR i.description LIKE %s)"
            )
            params.extend([f'%{search}%'] * 3)

        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        # Validate sort column to prevent injection
        valid_sorts = {
            'created_at': 'i.created_at',
            'priority': 'i.priority',
            'status': 'i.status',
            'title': 'i.title',
            'case_id': 'i.case_id',
        }
        sort_col = valid_sorts.get(sort_by, 'i.created_at')
        direction = 'ASC' if sort_dir.upper() == 'ASC' else 'DESC'

        total = fetch_one(
            f"SELECT COUNT(*) AS cnt FROM incidents i{where}", params
        )['cnt']

        offset = (page - 1) * per_page
        params.extend([per_page, offset])
        rows = fetch_all(
            f"""SELECT i.*, u.full_name AS reporter_name,
                       o.full_name AS officer_name,
                       ic.name     AS category_name
                FROM incidents i
                JOIN users u ON i.user_id = u.id
                LEFT JOIN users o ON i.assigned_officer_id = o.id
                LEFT JOIN incident_categories ic ON i.category_id = ic.id
                {where}
                ORDER BY {sort_col} {direction}
                LIMIT %s OFFSET %s""",
            params
        )
        return rows, total

    # ── Status Management ──────────────────────────────────────────
    @staticmethod
    def update_status(incident_id, new_status, changed_by, notes=None):
        """Update incident status and record in history."""
        current = fetch_one(
            "SELECT status FROM incidents WHERE id = %s", (incident_id,)
        )
        if not current:
            return False

        old_status = current['status']

        execute(
            "UPDATE incidents SET status = %s WHERE id = %s",
            (new_status, incident_id)
        )
        execute(
            """INSERT INTO case_status_history
                (incident_id, old_status, new_status, changed_by, notes)
               VALUES (%s, %s, %s, %s, %s)""",
            (incident_id, old_status, new_status, changed_by, notes)
        )
        return True

    # ── Officer Assignment ─────────────────────────────────────────
    @staticmethod
    def assign_officer(incident_id, officer_user_id, assigned_by):
        """Assign an officer and set status to 'Assigned'."""
        execute(
            "UPDATE incidents SET assigned_officer_id = %s, status = 'Assigned' WHERE id = %s",
            (officer_user_id, incident_id)
        )
        # Record the status change
        execute(
            """INSERT INTO case_status_history
                (incident_id, old_status, new_status, changed_by, notes)
               VALUES (%s, 'Pending', 'Assigned', %s, %s)""",
            (incident_id, assigned_by, f'Assigned to officer ID {officer_user_id}')
        )

    # ── Priority ───────────────────────────────────────────────────
    @staticmethod
    def update_priority(incident_id, priority):
        execute(
            "UPDATE incidents SET priority = %s WHERE id = %s",
            (priority, incident_id)
        )

    # ── Resolution ─────────────────────────────────────────────────
    @staticmethod
    def set_resolution(incident_id, remarks):
        execute(
            "UPDATE incidents SET resolution_remarks = %s WHERE id = %s",
            (remarks, incident_id)
        )

    # ── Timeline ───────────────────────────────────────────────────
    @staticmethod
    def get_timeline(incident_id):
        """Return status change history for an incident."""
        return fetch_all(
            """SELECT csh.*, u.full_name AS changed_by_name
               FROM case_status_history csh
               JOIN users u ON csh.changed_by = u.id
               WHERE csh.incident_id = %s
               ORDER BY csh.created_at ASC""",
            (incident_id,)
        )

    # ── Investigation Notes ────────────────────────────────────────
    @staticmethod
    def get_notes(incident_id):
        return fetch_all(
            """SELECT n.*, u.full_name AS officer_name
               FROM investigation_notes n
               JOIN users u ON n.officer_id = u.id
               WHERE n.incident_id = %s
               ORDER BY n.created_at DESC""",
            (incident_id,)
        )

    @staticmethod
    def add_note(incident_id, officer_id, note):
        return execute(
            """INSERT INTO investigation_notes (incident_id, officer_id, note)
               VALUES (%s, %s, %s)""",
            (incident_id, officer_id, note)
        )

    # ── Statistics ─────────────────────────────────────────────────
    @staticmethod
    def count(status=None, officer_id=None):
        conditions = []
        params = []
        if status:
            conditions.append("status = %s")
            params.append(status)
        if officer_id:
            conditions.append("assigned_officer_id = %s")
            params.append(officer_id)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        row = fetch_one(f"SELECT COUNT(*) AS cnt FROM incidents{where}", params)
        return row['cnt'] if row else 0

    @staticmethod
    def monthly_stats(year=None):
        """Return incident counts grouped by month for a given year."""
        if not year:
            year = datetime.now().year
        return fetch_all(
            """SELECT CAST(strftime('%m', created_at) AS INTEGER) AS month, COUNT(*) AS count
               FROM incidents
               WHERE CAST(strftime('%Y', created_at) AS INTEGER) = %s
               GROUP BY month
               ORDER BY month""",
            (year,)
        )

    @staticmethod
    def category_stats():
        """Return incident counts grouped by category."""
        return fetch_all(
            """SELECT COALESCE(ic.name, 'Uncategorized') AS category, COUNT(*) AS count
               FROM incidents i
               LEFT JOIN incident_categories ic ON i.category_id = ic.id
               GROUP BY ic.name
               ORDER BY count DESC"""
        )

    @staticmethod
    def priority_stats():
        """Return incident counts grouped by priority."""
        return fetch_all(
            """SELECT priority, COUNT(*) AS count
               FROM incidents
               GROUP BY priority"""
        )

    @staticmethod
    def daily_stats(days=30):
        """Return incident counts for the last N days."""
        return fetch_all(
            """SELECT DATE(created_at) AS date, COUNT(*) AS count
               FROM incidents
               WHERE created_at >= datetime('now', '-' || %s || ' days')
               GROUP BY DATE(created_at)
               ORDER BY date""",
            (days,)
        )

    @staticmethod
    def resolution_rate():
        """Return counts of resolved/closed vs total."""
        total = fetch_one("SELECT COUNT(*) AS cnt FROM incidents")['cnt']
        resolved = fetch_one(
            "SELECT COUNT(*) AS cnt FROM incidents WHERE status IN ('Resolved', 'Closed')"
        )['cnt']
        return {'total': total, 'resolved': resolved, 'rate': round(resolved / total * 100, 1) if total else 0}
