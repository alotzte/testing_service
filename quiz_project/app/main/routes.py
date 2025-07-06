from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

# Создаем Blueprint 'main'
main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route('/')
def index():
    """
    Главная страница-распределитель.
    """
    # Проверяем, аутентифицирован ли текущий пользователь.
    # `current_user` - это специальный объект от Flask-Login.
    if current_user.is_authenticated:
        # Если пользователь вошел в систему, показываем ему
        # новую главную страницу для залогиненных.
        return render_template('main/index.html', title='Главная')
    else:
        # Если пользователь НЕ вошел (анонимный),
        # перенаправляем его на страницу входа.
        return redirect(url_for('auth.login'))
