from . import db, login_manager  # Импортируем db и login_manager из __init__.py
from flask_login import UserMixin  # Импортируем специальный класс для моделей пользователей
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON

# Эта функция-загрузчик пользователя нужна для Flask-Login.
# Она будет вызываться при каждом запросе, чтобы получить объект
# текущего пользователя из БД по его ID, который хранится в сессии.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    """
    Класс User представляет таблицу пользователей в базе данных.
    db.Model - это базовый класс для всех моделей от Flask-SQLAlchemy.
    UserMixin - это класс от Flask-Login, который добавляет стандартные
    атрибуты и методы для управления сессией пользователя (is_authenticated и т.д.).
    """
    # Определяем столбцы (поля) нашей таблицы

    # id: Уникальный идентификатор пользователя. Первичный ключ.
    id = db.Column(db.Integer, primary_key=True)

    # username: Имя пользователя. Должно быть уникальным и не может быть пустым.
    username = db.Column(db.String(80), unique=True, nullable=False)

    # password_hash: Хеш пароля
    # Мы будем хранить только результат хеширования.
    password_hash = db.Column(db.String(128), nullable=False)

    # role: Роль пользователя ('user' или 'admin'). По умолчанию - 'user'.
    role = db.Column(db.String(20), nullable=False, default='user')
    group = db.Column(db.String(7), default="")
    def set_password(self, password):
        """Метод для установки хеша пароля."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Метод для проверки пароля."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Метод для представления объекта User в виде строки (удобно для отладки)."""
        return f'<User {self.username}>'

class Test(db.Model):
    __tablename__ = 'tests'  # Изменяем имя таблицы на 'tests'
    id = db.Column(db.Integer, primary_key=True)
    test_author = db.Column(db.String(80), nullable=False)
    test_info = db.Column(db.Text)  # Для SQLite используем Text вместо JSON
    groups = db.Column(db.Text)  # Переименовано с test_groups на groups

class TestResult(db.Model):
    __tablename__ = 'test_results'
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_result = db.Column(db.Text)  # Для SQLite используем Text вместо JSON для хранения результатов
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_graded = db.Column(db.Boolean, default=False)  # Флаг, указывающий, проверен ли тест вручную
    manual_score = db.Column(db.Integer, nullable=True)  # Оценка, выставленная вручную
    graded_at = db.Column(db.DateTime, nullable=True)  # Когда был проверен тест
    graded_by = db.Column(db.String(80), nullable=True)  # Кто проверил тест
    
    # Определяем отношения для удобства доступа
    test = db.relationship('Test', backref=db.backref('results', lazy=True))
    student = db.relationship('User', backref=db.backref('test_results', lazy=True))
    
    def __repr__(self):
        return f'<TestResult {self.id}: Test {self.test_id} by Student {self.student_id}>'