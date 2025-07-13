from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

# --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
# Находим абсолютный путь к папке, где находится этот файл (__init__.py)
basedir = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__, instance_relative_config=False)  # instance_relative_config можно выключить

    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    # Создаем надежный, абсолютный путь к файлу базы данных
    db_path = os.path.join(basedir, '../instance/site.db')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'my-super-secret-key-for-dev')
    # Указываем новый, абсолютный путь
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Эта настройка может помочь с ошибкой "database is locked"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_timeout': 30}

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Пожалуйста, войдите, чтобы получить доступ к этой странице."
    login_manager.login_message_category = "info"

    with app.app_context():
        # Убедимся, что папка instance существует
        instance_path = os.path.join(basedir, '../instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
            
        # Импортируем модели, чтобы они были доступны для создания таблиц
        from .models import User, Test
        
        # Пересоздаем все таблицы для обновления структуры
        db.drop_all()  # Удаляем все существующие таблицы
        db.create_all()  # Создаем таблицы заново с новой структурой
        
        # Создаем тестового администратора после пересоздания таблиц
        try:
            from .models import User
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', role='admin', group='')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
        except Exception as e:
            print(f"Ошибка при создании тестового администратора: {e}")

        # Импортируем и регистрируем Blueprints
        from .main.routes import main_bp
        app.register_blueprint(main_bp)
        
        from .auth.routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        
        from .creating_tests.routes import creating_tests_bp
        app.register_blueprint(creating_tests_bp)
        
        # Регистрируем админский blueprint
        from .admin.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
    return app
