from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Acesso negado: Você não possui permissão de administrador para realizar esta ação.', 'error')
            
            return redirect(url_for('dashboard.dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function