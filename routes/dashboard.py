"""
Dashboard routes — role-based redirect and user dashboard.
"""
from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from models.incident import Incident
from models.notification import Notification

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Redirect to the appropriate dashboard based on user role."""
    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif current_user.role == 'officer':
        return redirect(url_for('officer.officer_dashboard'))
    else:
        return redirect(url_for('dashboard.user_dashboard'))


@dashboard_bp.route('/dashboard/user')
@login_required
def user_dashboard():
    """Citizen dashboard — recent cases, stats, notifications."""
    total = Incident.count(officer_id=None)  # All user's cases counted below
    # Get user's cases
    from database import fetch_one
    my_total = fetch_one(
        "SELECT COUNT(*) AS cnt FROM incidents WHERE user_id = %s",
        (current_user.id,)
    )['cnt']
    my_pending = fetch_one(
        "SELECT COUNT(*) AS cnt FROM incidents WHERE user_id = %s AND status = 'Pending'",
        (current_user.id,)
    )['cnt']
    my_resolved = fetch_one(
        "SELECT COUNT(*) AS cnt FROM incidents WHERE user_id = %s AND status IN ('Resolved', 'Closed')",
        (current_user.id,)
    )['cnt']
    my_active = fetch_one(
        "SELECT COUNT(*) AS cnt FROM incidents WHERE user_id = %s AND status IN ('Assigned', 'Under Investigation')",
        (current_user.id,)
    )['cnt']

    recent_cases, _ = Incident.get_all(page=1, per_page=5, user_id=current_user.id)
    notifications = Notification.get_for_user(current_user.id, limit=10)
    unread_count = Notification.count_unread(current_user.id)

    return render_template('dashboard/user.html',
                           my_total=my_total,
                           my_pending=my_pending,
                           my_resolved=my_resolved,
                           my_active=my_active,
                           recent_cases=recent_cases,
                           notifications=notifications,
                           unread_count=unread_count)


@dashboard_bp.route('/notifications/count')
@login_required
def notification_count():
    """API endpoint for polling unread notification count."""
    count = Notification.count_unread(current_user.id)
    return jsonify({'count': count})


@dashboard_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read."""
    Notification.mark_all_read(current_user.id)
    return jsonify({'status': 'ok'})
