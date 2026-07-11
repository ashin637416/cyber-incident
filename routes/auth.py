"""
Authentication routes — registration, login, logout, profile, password change.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from utils.helpers import validate_email, validate_phone, validate_password, sanitize_input, log_audit

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Citizen registration."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = sanitize_input(request.form.get('full_name', ''))
        email = sanitize_input(request.form.get('email', '')).lower()
        phone = sanitize_input(request.form.get('phone', ''))
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not full_name or len(full_name) < 2:
            errors.append('Full name is required (min 2 characters).')
        if not validate_email(email):
            errors.append('Please enter a valid email address.')
        if phone and not validate_phone(phone):
            errors.append('Please enter a valid phone number.')

        valid_pwd, pwd_msg = validate_password(password)
        if not valid_pwd:
            errors.append(pwd_msg)
        if password != confirm:
            errors.append('Passwords do not match.')

        # Check if email already exists
        if User.get_by_email(email):
            errors.append('An account with this email already exists.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/register.html')

        # Create user
        try:
            user_id = User.create(full_name, email, phone or None, password, role='citizen')
            log_audit(user_id, 'USER_REGISTERED', f'New citizen: {email}')
            flash('Account created successfully! Please sign in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
            return render_template('auth/register.html')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login (all roles)."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', '')).lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'warning')
            return render_template('auth/login.html')

        user = User.get_by_email(email)
        if not user:
            flash('You need to register first.', 'danger')
            return render_template('auth/login.html')

        authenticated_user = User.verify_password(email, password)
        if authenticated_user:
            if not authenticated_user.is_active:
                flash('Your account has been deactivated. Contact admin.', 'danger')
                return render_template('auth/login.html')

            login_user(authenticated_user)
            log_audit(authenticated_user.id, 'USER_LOGIN', f'Login: {email}')
            flash(f'Welcome back, {authenticated_user.full_name}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Your password or username is incorrect.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log the user out and redirect to login."""
    log_audit(current_user.id, 'USER_LOGOUT', f'Logout: {current_user.email}')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit profile, change password."""
    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'profile':
            full_name = sanitize_input(request.form.get('full_name', ''))
            phone = sanitize_input(request.form.get('phone', ''))
            address = sanitize_input(request.form.get('address', ''))

            if not full_name or len(full_name) < 2:
                flash('Full name is required.', 'danger')
                return render_template('auth/profile.html')

            User.update_profile(current_user.id, full_name, phone or None, address or None)
            log_audit(current_user.id, 'PROFILE_UPDATED', 'Profile details updated')
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))

        elif form_type == 'password':
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_new = request.form.get('confirm_new_password', '')

            if not User.check_current_password(current_user.id, current_password):
                flash('Current password is incorrect.', 'danger')
                return render_template('auth/profile.html')

            valid_pwd, pwd_msg = validate_password(new_password)
            if not valid_pwd:
                flash(pwd_msg, 'danger')
                return render_template('auth/profile.html')

            if new_password != confirm_new:
                flash('New passwords do not match.', 'danger')
                return render_template('auth/profile.html')

            User.change_password(current_user.id, new_password)
            log_audit(current_user.id, 'PASSWORD_CHANGED', 'Password updated')
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
