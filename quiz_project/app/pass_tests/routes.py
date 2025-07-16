from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import traceback

from ..forms import RegistrationForm, LoginForm
from ..models import User, Test, TestResult
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
        return render_template('pass_tests/my_tests.html', available_tests=[], completed_tests=[])
    
    # Получаем все тесты
    all_tests = Test.query.all()
    
    # Фильтруем тесты, доступные для группы пользователя
    available_tests = []
    for test in all_tests:
        try:
            # Загружаем список групп из JSON строки
            test_groups = json.loads(test.groups)
            
            # Проверяем, входит ли группа пользователя в список групп теста
            if user_group in test_groups:
                # Получаем информацию о тесте
                test_info = json.loads(test.test_info)
                available_tests.append({
                    'id': test.id,
                    'name': test_info.get('name', 'Без названия'),
                    'author': test.test_author,
                    'questions_count': len(test_info.get('questions', [])),
                })
        except (json.JSONDecodeError, AttributeError) as e:
            # Пропускаем тесты с некорректными данными
            print(f"Ошибка при обработке теста: {str(e)}")
            continue
    
    # Получаем список пройденных пользователем тестов
    completed_tests = TestResult.query.filter_by(student_id=current_user.id).all()
    
    # Создаем словарь с id теста и id результата
    completed_test_ids = {}
    for result in completed_tests:
        completed_test_ids[result.test_id] = result.id
    
    # Добавляем информацию о результатах к доступным тестам
    for test in available_tests:
        if test['id'] in completed_test_ids:
            test['result_id'] = completed_test_ids[test['id']]
    
    return render_template('pass_tests/my_tests.html', 
                          available_tests=available_tests,
                          completed_test_ids=completed_test_ids)


@pass_tests_bp.route('/take_test/<int:test_id>', methods=['GET', 'POST'])
@login_required
def take_test(test_id):
    # Получаем тест из базы данных
    test = Test.query.get_or_404(test_id)
    
    # Проверяем, имеет ли пользователь доступ к этому тесту
    try:
        test_groups = json.loads(test.groups)
        if current_user.group not in test_groups:
            flash('У вас нет доступа к этому тесту.', 'danger')
            return redirect(url_for('pass_tests.my_tests'))
    except (json.JSONDecodeError, AttributeError) as e:
        flash(f'Ошибка при загрузке теста: {str(e)}', 'danger')
        return redirect(url_for('pass_tests.my_tests'))
    
    # Загружаем информацию о тесте
    try:
        test_info = json.loads(test.test_info)
        print(f"DEBUG - Формат теста: {test_info}")
        
        # Преобразуем формат данных для шаблона, если необходимо
        questions = test_info.get('questions', [])
        
        # Преобразуем формат вопросов для совместимости с шаблоном
        for i, question in enumerate(questions):
            # Определяем тип вопроса
            if question.get('type') == 'multiple_choice':
                # Вопрос с вариантами ответов
                question['type'] = 'single'  # или 'multiple' в зависимости от логики
                
                # Получаем варианты ответов
                answers = question.get('answers', [])
                options = [answer.get('text', '') for answer in answers]
                question['options'] = options
                
                # Находим правильный ответ
                correct_answer_index = question.get('correctAnswerIndex', -1)
                if correct_answer_index >= 0 and correct_answer_index < len(options):
                    question['correct_answer'] = options[correct_answer_index]
                else:
                    question['correct_answer'] = ''
                
                # Добавляем текст вопроса, если его нет
                if not question.get('text'):
                    question['text'] = question.get('question', 'Без текста')
                
            elif question.get('type') == 'text_answer':
                # Вопрос с текстовым ответом
                question['type'] = 'text'
                question['correct_answer'] = question.get('textAnswer', '')
                
                # Добавляем текст вопроса, если его нет
                if not question.get('text'):
                    question['text'] = question.get('question', 'Без текста')
        
        print(f"DEBUG - Преобразованные вопросы: {questions}")
    except Exception as e:
        print(f"DEBUG - Ошибка при обработке теста: {str(e)}")
        print(traceback.format_exc())
        flash(f'Ошибка при загрузке теста: {str(e)}', 'danger')
        return redirect(url_for('pass_tests.my_tests'))
    
    # Проверяем, не проходил ли пользователь уже этот тест
    existing_result = TestResult.query.filter_by(
        test_id=test_id, 
        student_id=current_user.id
    ).first()
    
    if existing_result:
        flash('Вы уже проходили этот тест.', 'info')
        return redirect(url_for('pass_tests.view_result', result_id=existing_result.id))
    
    if request.method == 'POST':
        # Получаем ответы пользователя
        answers = request.form.to_dict()
        print(f"DEBUG - Полученные ответы: {answers}")
        
        # Проверяем ответы
        score = 0
        total_questions = len(questions)
        results = []
        
        for i, question in enumerate(questions):
            question_id = f'question_{i}'
            question_type = question.get('type', '')
            
            # Обработка разных типов вопросов
            if question_type == 'single':
                # Вопрос с одним ответом
                user_answer = answers.get(question_id, '')
                correct_answer = question.get('correct_answer', '')
                correct = user_answer == correct_answer
                
                if correct:
                    score += 1
                
                results.append({
                    'question': question.get('text', ''),
                    'type': 'single',
                    'options': question.get('options', []),
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': correct
                })
                
            elif question_type == 'multiple':
                # Вопрос с множественным выбором
                user_answers = request.form.getlist(question_id)
                correct_answers = question.get('correct_answers', [])
                correct = set(user_answers) == set(correct_answers)
                
                if correct:
                    score += 1
                
                results.append({
                    'question': question.get('text', ''),
                    'type': 'multiple',
                    'options': question.get('options', []),
                    'user_answer': user_answers,
                    'correct_answer': correct_answers,
                    'is_correct': correct
                })
                
            elif question_type == 'text':
                # Вопрос с текстовым ответом
                user_answer = answers.get(question_id, '').strip()
                correct_answer = question.get('correct_answer', '').strip()
                
                # Проверка ответа без учета регистра
                correct = user_answer.lower() == correct_answer.lower()
                
                if correct:
                    score += 1
                
                results.append({
                    'question': question.get('text', ''),
                    'type': 'text',
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': correct
                })
        
        # Формируем результат теста
        test_result = {
            'score': score,
            'total': total_questions,
            'percentage': round((score / total_questions) * 100) if total_questions > 0 else 0,
            'questions': results,
            'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Сохраняем результат в базу данных
        new_result = TestResult(
            test_id=test_id,
            student_id=current_user.id,
            test_result=json.dumps(test_result, ensure_ascii=False)
        )
        
        db.session.add(new_result)
        db.session.commit()
        
        flash('Тест успешно пройден!', 'success')
        return redirect(url_for('pass_tests.view_result', result_id=new_result.id))
    
    return render_template('pass_tests/take_test.html', test=test, test_info=test_info)


@pass_tests_bp.route('/results')
@login_required
def results():
    # Получаем все результаты тестов текущего пользователя
    user_results = TestResult.query.filter_by(student_id=current_user.id).all()
    
    results_data = []
    for result in user_results:
        test = Test.query.get(result.test_id)
        if test:
            test_info = json.loads(test.test_info)
            result_data = json.loads(result.test_result)
            
            results_data.append({
                'id': result.id,
                'test_name': test_info.get('name', 'Без названия'),
                'score': result_data.get('score', 0),
                'total': result_data.get('total', 0),
                'percentage': result_data.get('percentage', 0),
                'completed_at': result_data.get('completed_at', '')
            })
    
    return render_template('pass_tests/results.html', results=results_data)


@pass_tests_bp.route('/result/<int:result_id>')
@login_required
def view_result(result_id):
    # Получаем результат теста
    result = TestResult.query.get_or_404(result_id)
    
    # Проверяем, принадлежит ли результат текущему пользователю или администратору
    if result.student_id != current_user.id and current_user.role != 'admin':
        flash('У вас нет доступа к этому результату.', 'danger')
        return redirect(url_for('pass_tests.results'))
    
    # Получаем информацию о тесте
    test = Test.query.get(result.test_id)
    if not test:
        flash('Тест не найден.', 'danger')
        return redirect(url_for('pass_tests.results'))
    
    test_info = json.loads(test.test_info)
    result_data = json.loads(result.test_result)
    
    return render_template('pass_tests/view_result.html', 
                          test_name=test_info.get('name', 'Без названия'),
                          test_author=test.test_author,
                          result=result_data,
                          student=User.query.get(result.student_id))
