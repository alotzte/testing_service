from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user


from ..forms import RegistrationForm, LoginForm
from ..models import User, Test
from .. import db
import json

pass_tests_bp = Blueprint('pass_tests', __name__, template_folder='templates')


@pass_tests_bp.route('/my_tests', methods=['GET', 'POST'])
@login_required
def my_tests():
    # Получаем группу текущего пользователя
    user_group = current_user.group
    
    # Если у пользователя не указана группа, показываем сообщение
    if not user_group:
        flash('У вас не указана группа. Доступных тестов нет.', 'warning')
        return render_template('pass_tests/my_tests.html', available_tests=[])
    
    # Получаем все тесты из базы данных
    all_tests = Test.query.all()
    
    # Фильтруем тесты, доступные для группы пользователя
    available_tests = []
    for test in all_tests:
        try:
            # Загружаем список групп из JSON строки
            test_groups = json.loads(test.groups)
            
            # Проверяем, входит ли группа пользователя в список групп теста
            if user_group in test_groups:
                # Загружаем информацию о тесте
                test_info = json.loads(test.test_info)
                
                # Добавляем тест в список доступных
                available_tests.append({
                    'id': test.id,
                    'name': test_info.get('name', 'Без названия'),
                    'author': test.test_author,
                    'questions_count': len(test_info.get('questions', []))
                })
        except Exception as e:
            # Если возникла ошибка при обработке теста, пропускаем его
            print(f"Ошибка при обработке теста {test.id}: {str(e)}")
            continue
    
    return render_template('pass_tests/my_tests.html', available_tests=available_tests)

@pass_tests_bp.route('/take_test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def take_test(test_id):
    """
    Страница для прохождения теста
    """
    # Получаем тест из базы данных
    test = Test.query.get_or_404(test_id)
    
    # Проверяем, имеет ли пользователь доступ к этому тесту
    try:
        test_groups = json.loads(test.groups)
        if current_user.group not in test_groups:
            flash('У вас нет доступа к этому тесту.', 'danger')
            return redirect(url_for('pass_tests.my_tests'))
    except Exception as e:
        flash(f'Ошибка при проверке доступа: {str(e)}', 'danger')
        return redirect(url_for('pass_tests.my_tests'))
    
    # Загружаем информацию о тесте
    try:
        test_info = json.loads(test.test_info)
    except Exception as e:
        flash(f'Ошибка при загрузке теста: {str(e)}', 'danger')
        return redirect(url_for('pass_tests.my_tests'))
    
    # Заглушка для страницы прохождения теста
    return render_template('pass_tests/take_test.html', test=test, test_info=test_info)
