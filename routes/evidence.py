"""
Evidence routes — upload, download, delete, notes.
"""
import os
from flask import Blueprint, request, redirect, url_for, flash, send_file, jsonify
from flask_login import login_required, current_user
from models.evidence import Evidence
from models.incident import Incident
from utils.helpers import log_audit, format_file_size
from utils.decorators import officer_required
from config import Config

evidence_bp = Blueprint('evidence', __name__)


@evidence_bp.route('/evidence/upload/<int:incident_id>', methods=['POST'])
@login_required
def upload_evidence(incident_id):
    """Upload evidence files for an incident."""
    incident = Incident.get_by_id(incident_id)
    if not incident:
        flash('Incident not found.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    # Access: owner, assigned officer, or admin
    if (current_user.role == 'citizen' and incident['user_id'] != current_user.id):
        flash('Access denied.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    files = request.files.getlist('evidence_files')
    uploaded = 0
    for f in files:
        if f and f.filename:
            try:
                Evidence.save_file(f, incident_id, current_user.id)
                uploaded += 1
            except ValueError as ve:
                flash(f'File error ({f.filename}): {ve}', 'warning')

    if uploaded > 0:
        log_audit(current_user.id, 'EVIDENCE_UPLOADED',
                  f'{uploaded} file(s) uploaded for case {incident["case_id"]}')
        flash(f'{uploaded} file(s) uploaded successfully!', 'success')
    else:
        flash('No files were uploaded.', 'warning')

    return redirect(url_for('incident.view_incident', incident_id=incident_id))


@evidence_bp.route('/evidence/download/<int:evidence_id>')
@login_required
def download_evidence(evidence_id):
    """Download an evidence file."""
    ev = Evidence.get_by_id(evidence_id)
    if not ev:
        flash('Evidence not found.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    # Access check
    incident = Incident.get_by_id(ev['incident_id'])
    if current_user.role == 'citizen' and incident['user_id'] != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    file_path = os.path.join(os.path.dirname(Config.UPLOAD_FOLDER), ev['file_path'])
    if not os.path.exists(file_path):
        flash('File not found on server.', 'danger')
        return redirect(url_for('incident.view_incident', incident_id=ev['incident_id']))

    log_audit(current_user.id, 'EVIDENCE_DOWNLOADED', f'Downloaded: {ev["original_name"]}')
    return send_file(file_path, as_attachment=True, download_name=ev['original_name'])


@evidence_bp.route('/evidence/<int:evidence_id>/delete', methods=['POST'])
@login_required
def delete_evidence(evidence_id):
    """Delete evidence (officers and admins only)."""
    if current_user.role == 'citizen':
        flash('Access denied.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    ev = Evidence.get_by_id(evidence_id)
    if not ev:
        flash('Evidence not found.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    incident_id = ev['incident_id']
    Evidence.delete(evidence_id)
    log_audit(current_user.id, 'EVIDENCE_DELETED', f'Deleted evidence: {ev["original_name"]}')
    flash('Evidence deleted.', 'success')
    return redirect(url_for('incident.view_incident', incident_id=incident_id))


@evidence_bp.route('/evidence/<int:evidence_id>/notes', methods=['POST'])
@login_required
def add_evidence_notes(evidence_id):
    """Add notes to evidence."""
    if current_user.role == 'citizen':
        flash('Access denied.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    ev = Evidence.get_by_id(evidence_id)
    if not ev:
        flash('Evidence not found.', 'danger')
        return redirect(url_for('incident.list_incidents'))

    notes = request.form.get('notes', '').strip()
    if notes:
        Evidence.update_notes(evidence_id, notes)
        flash('Evidence notes updated.', 'success')

    return redirect(url_for('incident.view_incident', incident_id=ev['incident_id']))
