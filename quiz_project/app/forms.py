from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from .models import User


class RegistrationForm(FlaskForm):
    """Класс для формы регистрации."""

    # Поле для ввода логина.
    # 'Логин' - это метка (label), которая будет отображаться рядом с полем.
    # validators - это список проверок, которые нужно применить к данным.
    username = StringField('Логин', validators=[
        DataRequired(message="Это поле не может быть пустым."),
        Length(min=4, max=25, message="Логин должен содержать от 4 до 25 символов.")
    ])

    # Поле для ввода пароля.
    password = PasswordField('Пароль', validators=[
        DataRequired(message="Это поле не может быть пустым."),
        Length(min=6, message="Пароль должен быть не менее 6 символов.")
    ])

    # Поле для подтверждения пароля.
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message="Это поле не может быть пустым."),
        EqualTo('password', message="Пароли должны совпадать.")  # Проверяет, что значение совпадает с полем 'password'
    ])

    # Поле для выбора роли.
    role = SelectField('Роль', choices=[('user', 'Пользователь'), ('admin', 'Администратор')],
                       validators=[DataRequired()])

    # Кнопка для отправки формы.
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        """
        Кастомный валидатор для проверки уникальности имени пользователя.
        WTForms автоматически находит методы, начинающиеся с validate_<имя_поля>,
        и выполняет их при валидации.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято. Пожалуйста, выберите другое.')


class LoginForm(FlaskForm):
    """Класс для формы входа."""
    # Поле для ввода логина. Проверяем только то, что оно не пустое.
    username = StringField('Логин', validators=[DataRequired(message="Введите ваш логин.")])

    # Поле для ввода пароля.
    password = PasswordField('Пароль', validators=[DataRequired(message="Введите ваш пароль.")])

    # Галочка "Запомнить меня".
    # BooleanField - это и есть чекбокс.
    remember_me = BooleanField('Запомнить меня')

    # Кнопка для отправки формы.
    submit = SubmitField('Войти')
