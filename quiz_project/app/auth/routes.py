from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

# Используем ваш стиль относительных импортов
from ..forms import RegistrationForm, LoginForm
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


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Если пользователь уже вошел, ему не нужно на страницу входа
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # 1. Ищем пользователя в базе данных по введенному логину
        user = User.query.filter_by(username=form.username.data).first()

        # 2. Проверяем, что пользователь существует И введенный пароль верный
        #    Для этого используем метод check_password, который мы создали в модели User
        if user and user.check_password(form.password.data):
            # 3. Если все верно, "запоминаем" пользователя
            #    Функция login_user из Flask-Login делает всю магию с сессиями.
            #    remember=form.remember_me.data - передаем значение галочки "Запомнить меня"
            login_user(user, remember=form.remember_me.data)

            # Flask-Login может запомнить, куда пользователь хотел попасть до того,
            # как его отправили на страницу логина. `request.args.get('next')`
            # позволяет перенаправить его туда после успешного входа.
            next_page = request.args.get('next')
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            # 4. Если пользователь не найден или пароль неверный - показываем ошибку
            flash('Неверный логин или пароль. Пожалуйста, попробуйте снова.', 'danger')

    return render_template('auth/login.html', title='Вход', form=form)


# --- НОВАЯ ЛОГИКА ДЛЯ ВЫХОДА ---
@auth_bp.route('/logout')
@login_required  # Этот декоратор означает, что на эту страницу может зайти только авторизованный пользователь
def logout():
    # Функция logout_user() из Flask-Login "забывает" пользователя
    logout_user()
    flash('Вы успешно вышли из своего аккаунта.', 'info')
    return redirect(url_for('main.index'))
