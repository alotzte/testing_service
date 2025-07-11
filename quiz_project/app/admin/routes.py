from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

# Create admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates')

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and has admin role
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('У вас нет доступа к этой странице. Требуются права администратора.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard - main admin control panel
    """
    # Перенаправляем на главную страницу вместо показа dashboard.html
    return redirect(url_for('main.index'))
