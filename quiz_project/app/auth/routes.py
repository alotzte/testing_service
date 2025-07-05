from flask import Blueprint, render_template, redirect, url_for, flash

# Используем ваш стиль относительных импортов
from ..forms import RegistrationForm
from ..models import User
from .. import db

# Создаем Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Обрабатывает регистрацию нового пользователя."""
    form = RegistrationForm()

    if form.validate_on_submit():
        # Создаем нового пользователя
        new_user = User(
            username=form.username.data,
            role=form.role.data
        )
        new_user.set_password(form.password.data)

        # ДОБАВЛЕНО: Блок try...except для безопасного сохранения в БД
        try:
            # Добавляем нового пользователя в сессию базы данных
            db.session.add(new_user)
            # Сохраняем изменения в базе данных
            db.session.commit()

            # Показываем пользователю сообщение об успехе
            flash(f'Аккаунт для {form.username.data} успешно создан! Теперь вы можете войти.', 'success')

            # Перенаправляем на страницу входа
            return redirect(url_for('auth.login'))

        except Exception as e:
            # Если произошла ошибка, откатываем изменения и сообщаем об этом
            db.session.rollback()
            flash(f'Произошла ошибка при создании аккаунта: {e}', 'danger')

    # Если GET-запрос или форма невалидна, просто показываем страницу
    return render_template('auth/register.html', title='Регистрация', form=form)


# ДОБАВЛЕНО: "Заглушка" для страницы входа.
# Это необходимо, чтобы redirect(url_for('auth.login')) не вызывал ошибку.
@auth_bp.route('/login')
def login():
    return "<h1>Страница входа</h1><p>Будет реализована на следующем этапе.</p>"

