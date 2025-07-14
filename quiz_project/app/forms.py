from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, SelectField, IntegerField, FieldList, FormField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange, Optional
from .models import User, Test

def validate_group(form, field):  # form и field - обязательные аргументы для валидатора WTForms
    group = field.data
    role = form.role.data
    
    # Если роль администратор, устанавливаем пустую группу
    if role == "admin":
        field.data = ""
        return
    
    # Если пользователь не админ и группа не пустая, проверяем формат
    if group and (len(group) != 7 or group[0] not in ("Б", "М", "С") or group[3] != "-"):
        raise ValidationError("Введенная группа некорректна. Формат: Б00-000")

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
    role = RadioField('Роль', choices=[('user', 'Студент'), ('admin', 'Преподаватель')],
                       validators=[DataRequired()])

    # Поле для ввода группы
    group = StringField("Группа (например, Б23-302)", validators=[validate_group])

    # Кнопка для отправки формы.
    submit = SubmitField('Зарегистрироваться')
   # group = StringField("ggfg")
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


#For creating tests pohody nado budet vse delete
class AnswerVariantForm(FlaskForm):
    answer_variant = StringField('write variant of answer')
    correctness_of_answer = BooleanField('true or false')

class QuestionForm(FlaskForm):
    question_wording = StringField()
    type_of_answer = BooleanField('has this question one correct answer or many. True=one answer. False=many answers.')
    answers_list = FieldList(FormField(AnswerVariantForm), min_entries=2) #лист со всеми ответами(мин 2)

class TestCreatorForm(FlaskForm):
    duration_hours = IntegerField('hours', default=0)
    duration_minutes = IntegerField('minutes', validators=[ DataRequired(), NumberRange(min=0, max=59)])
    title_of_test = StringField('name of test')
 #   add_question = SubmitField('add question')
   # submit_test = SubmitField('save test')
    questions_list = FieldList(FormField(QuestionForm), min_entries=1) #лист со всеми вопросами(мин 1)

class CreateTestForm(FlaskForm):
    submit = SubmitField('save test')