# from . import db, login_manager  # Импортируем db и login_manager из __init__.py
# from flask_login import UserMixin  # Импортируем специальный класс для моделей пользователей
# from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.dialects.postgresql import JSON
#
# # Эта функция-загрузчик пользователя нужна для Flask-Login.
# # Она будет вызываться при каждом запросе, чтобы получить объект
# # текущего пользователя из БД по его ID, который хранится в сессии.
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
#
# class User(db.Model, UserMixin):
#     """
#     Класс User представляет таблицу пользователей в базе данных.
#     db.Model - это базовый класс для всех моделей от Flask-SQLAlchemy.
#     UserMixin - это класс от Flask-Login, который добавляет стандартные
#     атрибуты и методы для управления сессией пользователя (is_authenticated и т.д.).
#     """
#     # Определяем столбцы (поля) нашей таблицы
#
#     # id: Уникальный идентификатор пользователя. Первичный ключ.
#     id = db.Column(db.Integer, primary_key=True)
#
#     # username: Имя пользователя. Должно быть уникальным и не может быть пустым.
#     username = db.Column(db.String(80), unique=True, nullable=False)
#
#     # password_hash: Хеш пароля
#     # Мы будем хранить только результат хеширования.
#     password_hash = db.Column(db.String(128), nullable=False)
#
#     # role: Роль пользователя ('user' или 'admin'). По умолчанию - 'user'.
#     role = db.Column(db.String(20), nullable=False, default='user')
#     group = db.Column(db.String(7), default="")
#     def set_password(self, password):
#         """Метод для установки хеша пароля."""
#         self.password_hash = generate_password_hash(password)
#
#     def check_password(self, password):
#         """Метод для проверки пароля."""
#         return check_password_hash(self.password_hash, password)
#
#     def __repr__(self):
#         """Метод для представления объекта User в виде строки (удобно для отладки)."""
#         return f'<User {self.username}>'
#
# class Test(db.Model):
#     __tablename__ = 'tests'  # Изменяем имя таблицы на 'tests'
#     id = db.Column(db.Integer, primary_key=True)
#     test_author = db.Column(db.String(80), nullable=False)
#     test_info = db.Column(db.Text)  # Для SQLite используем Text вместо JSON




from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from passlib.context import CryptContext
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    full_name = Column(String(100), nullable=False)
    group_name = Column(String(50), nullable=True)

    authored_tests = relationship("TestAdmin", back_populates="author")
    student_tests = relationship("TestStudent", back_populates="student")


class TestAdmin(Base):
    __tablename__ = 'tests_admin'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    test_info = Column(JSON, nullable=False)

    author = relationship("User", back_populates="authored_tests")


class TestStudent(Base):
    __tablename__ = 'tests_students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    test_results = Column(JSON, nullable=False)

    student = relationship("User", back_populates="student_tests")


DATABASE_URL = "sqlite:///university.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseManager:
    def __init__(self):
        self.session = SessionLocal()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def user_exists(self, username: str) -> bool:
        return self.session.query(User).filter(User.username == username).first() is not None

    def create_user(self, username: str, password: str, role: str, full_name: str, group_name: str = None) -> User:
        new_user = User(
            username=username,
            password_hash=self.set_password(password),
            role=role,
            full_name=full_name,
            group_name=group_name
        )
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def get_user_by_id(self, user_id: int) -> User:
        return self.session.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> User:
        return self.session.query(User).filter(User.username == username).first()

    def update_user(self, user_id: int, **kwargs) -> User:
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if key == 'password':
                    setattr(user, 'password_hash', self.set_password(value))
                else:
                    setattr(user, key, value)
            self.session.commit()
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def set_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_test_admin(self, test_author_id: int, test_info: dict) -> TestAdmin:
        new_test = TestAdmin(
            test_author_id=test_author_id,
            test_info=test_info
        )
        self.session.add(new_test)
        self.session.commit()
        return new_test

    def get_test_admin(self, test_id: int) -> TestAdmin:
        return self.session.query(TestAdmin).filter(TestAdmin.id == test_id).first()

    def update_test_admin(self, test_id: int, test_info: dict) -> TestAdmin:
        test = self.get_test_admin(test_id)
        if test:
            test.test_info = test_info
            self.session.commit()
        return test

    def create_test_student(self, test_student_id: int, test_results: dict) -> TestStudent:
        new_test = TestStudent(
            test_student_id=test_student_id,
            test_results=test_results
        )
        self.session.add(new_test)
        self.session.commit()
        return new_test

    def get_test_student(self, test_id: int) -> TestStudent:
        return self.session.query(TestStudent).filter(TestStudent.id == test_id).first()

    def get_student_tests(self, student_id: int) -> list:
        return self.session.query(TestStudent).filter(TestStudent.test_student_id == student_id).all()

    def update_test_results(self, test_id: int, new_results: dict) -> TestStudent:
        test = self.get_test_student(test_id)
        if test:
            test.test_results = new_results
            self.session.commit()
        return test

    def close(self):
        self.session.close()


# Создаем экземпляр DatabaseManager
db = DatabaseManager()

# 1. Создаем пользователей (если они не существуют)
if not db.user_exists("professor_ivanov"):
    teacher = db.create_user(
        username="professor_ivanov",
        password="teacher123",
        role="teacher",
        full_name="Иванов Иван Иванович"
    )
else:
    teacher = db.get_user_by_username("professor_ivanov")
    print(f"Преподаватель {teacher.username} уже существует")

if not db.user_exists("student_petrov"):
    student1 = db.create_user(
        username="student_petrov",
        password="student123",
        role="student",
        full_name="Петров Петр Петрович",
        group_name="Группа 101"
    )
else:
    student1 = db.get_user_by_username("student_petrov")
    print(f"Студент {student1.username} уже существует")

if not db.user_exists("student_sidorova"):
    student2 = db.create_user(
        username="student_sidorova",
        password="student456",
        role="student",
        full_name="Сидорова Мария Сергеевна",
        group_name="Группа 101"
    )
else:
    student2 = db.get_user_by_username("student_sidorova")
    print(f"Студент {student2.username} уже существует")

# 2. Создаем тест от имени преподавателя
math_test = db.create_test_admin(
    test_author_id=teacher.id,
    test_info={
        "title": "Контрольная по математике",
        "questions": [
            {
                "question": "Сколько будет 2+2?",
                "options": ["3", "4", "5", "6"],
                "correct": 1
            },
            {
                "question": "Чему равен корень из 9?",
                "options": ["2", "3", "4", "5"],
                "correct": 1
            }
        ]
    }
)

# 3. Студенты проходят тест
db.create_test_student(
    test_student_id=student1.id,
    test_results={
        "test_id": math_test.id,
        "answers": [1, 1],
        "score": "100%"
    }
)

db.create_test_student(
    test_student_id=student2.id,
    test_results={
        "test_id": math_test.id,
        "answers": [0, 1],
        "score": "50%"
    }
)

# 4. Получаем данные и демонстрируем связи
teacher_from_db = db.get_user_by_id(teacher.id)
print(f"\nПреподаватель: {teacher_from_db.full_name}")
print("Созданные тесты:")
for test in teacher_from_db.authored_tests:
    print(f"- {test.test_info['title']}")

student_from_db = db.get_user_by_id(student1.id)
print(f"\nСтудент: {student_from_db.full_name}")
print("Пройденные тесты:")
for test in student_from_db.student_tests:
    test_admin = db.get_test_admin(test.test_results['test_id'])
    print(f"- {test_admin.test_info['title']}: {test.test_results['score']}")

# 5. Обновляем результаты теста
student1_tests = db.get_student_tests(student1.id)
if student1_tests:
    test_to_update = student1_tests[0]
    db.update_test_results(
        test_id=test_to_update.id,
        new_results={
            "test_id": math_test.id,
            "answers": [1, 1],
            "score": "100% (исправлено)"
        }
    )

# 6. Закрываем соединение
db.close()