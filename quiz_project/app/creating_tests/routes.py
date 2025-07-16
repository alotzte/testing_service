from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime

from ..models import User, Test, TestResult
from .. import db
import json
import traceback

creating_tests_bp = Blueprint('creating_tests', __name__, template_folder='templates')

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and has admin role
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('У вас нет доступа к этой странице. Требуются права администратора.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@creating_tests_bp.route('/creator', methods=['GET', 'POST'])
@login_required
def create_test():
    """
    Page for creating new tests
    """
    print("Request method:", request.method)
    
    if request.method == 'POST' and current_user.role != "user":
        print("Received POST request")
        try:
            # Проверяем, что запрос содержит JSON
            if not request.is_json:
                print("Request is not JSON")
                return jsonify({"success": False, "message": "Запрос должен содержать JSON"}), 400
                
            try:
                # Пробуем получить JSON из запроса
                received_data = request.get_json()
                print("Received data:", received_data)
                
                if not received_data:
                    return jsonify({"success": False, "message": "Пустые данные"}), 400
                
                # Store the author of the test
                received_data['author'] = current_user.username
                # Convert to JSON string for storage
                json_string_to_store = json.dumps(received_data, indent=2, ensure_ascii=False)
                print("JSON to store:", json_string_to_store)
                
                try:
                    # Create new test record
                    new_test = Test(
                        test_author=current_user.username,
                        test_info=json_string_to_store,
                        groups=json.dumps(received_data["groups"], ensure_ascii=False)
                    )
                    
                    # Save to database
                    db.session.add(new_test)
                    db.session.commit()
                    print("Test saved successfully")
                    
                    # Return success response
                    return jsonify({"success": True, "message": "Тест успешно сохранен"}), 200
                except Exception as e:
                    print("Database error:", str(e))
                    print(traceback.format_exc())
                    db.session.rollback()
                    return jsonify({"success": False, "message": f"Ошибка базы данных: {str(e)}"}), 500
            except Exception as e:
                print("JSON parsing error:", str(e))
                print(traceback.format_exc())
                return jsonify({"success": False, "message": f"Ошибка обработки JSON: {str(e)}"}), 400
        except Exception as e:
            print("General error:", str(e))
            print(traceback.format_exc())
            return jsonify({"success": False, "message": f"Общая ошибка: {str(e)}"}), 500
    
    # For GET requests, just render the template
    return render_template('creating_tests/index.html')

@creating_tests_bp.route('/my-tests', methods=['GET'])
@login_required
@admin_required
def my_tests():
    """
    Page for viewing and managing user's tests
    """
    # Get all tests created by the current user
    tests = Test.query.filter_by(test_author=current_user.username).all()
    
    # Parse the JSON data for each test
    parsed_tests = []
    for test in tests:
        try:
            test_data = json.loads(test.test_info)
            parsed_tests.append({
                'id': test.id,
                'name': test_data.get('name', 'Без названия'),
                'questions_count': len(test_data.get('questions', [])),
                'raw_data': test_data
            })
        except Exception as e:
            print(f"Error parsing test {test.id}: {str(e)}")
    
    return render_template('creating_tests/my_tests.html', tests=parsed_tests)

@creating_tests_bp.route('/test-results/<int:test_id>', methods=['GET'])
@login_required
@admin_required
def test_results(test_id):
    """
    Page for viewing all results for a specific test
    """
    # Get the test
    test = Test.query.get_or_404(test_id)
    
    # Check if the current user is the author
    if test.test_author != current_user.username:
        flash('У вас нет доступа к результатам этого теста.', 'danger')
        return redirect(url_for('creating_tests.my_tests'))
    
    # Get all results for this test
    results = TestResult.query.filter_by(test_id=test_id).all()
    
    # Parse test info
    test_info = json.loads(test.test_info)
    test_name = test_info.get('name', 'Без названия')
    
    # Prepare results data
    results_data = []
    for result in results:
        try:
            # Get student info
            student = User.query.get(result.student_id)
            
            # Parse result data
            result_data = json.loads(result.test_result)
            
            # Add to results list
            results_data.append({
                'id': result.id,
                'student_name': student.username if student else 'Неизвестный',
                'student_group': student.group if student else '',
                'score': result_data.get('score', 0),
                'total': result_data.get('total', 0),
                'percentage': result_data.get('percentage', 0),
                'completed_at': result_data.get('completed_at', '')
            })
        except Exception as e:
            print(f"Error parsing result {result.id}: {str(e)}")
    
    return render_template('creating_tests/test_results.html', 
                          test_id=test_id,
                          test_name=test_name,
                          results=results_data)

@creating_tests_bp.route('/edit-test/<int:test_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_test(test_id):
    """
    Page for editing an existing test
    """
    # Get the test
    test = Test.query.get_or_404(test_id)
    
    # Check if the current user is the author
    if test.test_author != current_user.username:
        flash('У вас нет доступа к редактированию этого теста.', 'danger')
        return redirect(url_for('creating_tests.my_tests'))
    
    if request.method == 'POST':
        try:
            if not request.is_json:
                return jsonify({"success": False, "message": "Запрос должен содержать JSON"}), 400
                
            received_data = request.get_json()
            
            if not received_data:
                return jsonify({"success": False, "message": "Пустые данные"}), 400
            
            # Preserve the author
            received_data['author'] = current_user.username
            
            # Update the test data
            json_string_to_store = json.dumps(received_data, indent=2, ensure_ascii=False)
            test.test_info = json_string_to_store
            groups_to_store = json.dumps(received_data["groups"], ensure_ascii=False)
            test.groups = groups_to_store
            # Save to database
            db.session.commit()
            
            return jsonify({"success": True, "message": "Тест успешно обновлен"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": f"Ошибка при обновлении теста: {str(e)}"}), 500
    
    # For GET requests, load the test data and render the edit template
    try:
        test_data = json.loads(test.test_info)
        return render_template('creating_tests/edit_test.html', test=test, test_data=test_data)
    except Exception as e:
        flash(f'Ошибка при загрузке теста: {str(e)}', 'danger')
        return redirect(url_for('creating_tests.my_tests'))

@creating_tests_bp.route('/delete-test/<int:test_id>', methods=['POST'])
@login_required
@admin_required
def delete_test(test_id):
    """
    Delete a test
    """
    test = Test.query.get_or_404(test_id)
    
    # Check if the current user is the author
    if test.test_author != current_user.username:
        return jsonify({"success": False, "message": "У вас нет доступа к удалению этого теста."}), 403
    
    try:
        db.session.delete(test)
        db.session.commit()
        return jsonify({"success": True, "message": "Тест успешно удален"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка при удалении теста: {str(e)}"}), 500

@creating_tests_bp.route('/grade-result/<int:result_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def grade_result(result_id):
    """
    Page for administrators to manually grade test results with open-ended answers
    """
    # Get the test result
    result = TestResult.query.get_or_404(result_id)
    
    # Get the test
    test = Test.query.get_or_404(result.test_id)
    
    # Check if the current user is the author of the test
    if test.test_author != current_user.username:
        flash('У вас нет доступа к этому результату теста.', 'danger')
        return redirect(url_for('creating_tests.my_tests'))
    
    # Get the student
    student = User.query.get(result.student_id)
    
    # Parse test info and result data
    test_info = json.loads(test.test_info)
    result_data = json.loads(result.test_result)
    
    # Check if there are any text questions
    has_text_questions = any(q.get('type') == 'text' for q in result_data.get('questions', []))
    
    if not has_text_questions:
        flash('В этом тесте нет вопросов с развернутым ответом для проверки.', 'info')
        return redirect(url_for('creating_tests.test_results', test_id=test.id))
    
    if request.method == 'POST':
        # Get the manual grades from the form
        try:
            # Initialize variables to track changes
            original_score = result_data.get('score', 0)
            additional_points = 0
            
            # Process each question
            for i, question in enumerate(result_data.get('questions', [])):
                if question.get('type') == 'text':
                    question_id = f'question_{i}'
                    is_correct = request.form.get(f'{question_id}_is_correct') == 'true'
                    feedback = request.form.get(f'{question_id}_feedback', '')
                    
                    # Update the question result
                    question['is_correct'] = is_correct
                    question['feedback'] = feedback
                    
                    # Add point if marked as correct and wasn't correct before
                    if is_correct and not question.get('is_correct', False):
                        additional_points += 1
                    # Remove point if marked as incorrect but was correct before
                    elif not is_correct and question.get('is_correct', False):
                        additional_points -= 1
            
            # Update the score
            new_score = original_score + additional_points
            result_data['score'] = new_score
            result_data['percentage'] = round((new_score / result_data.get('total', 1)) * 100)
            
            # Update the result in the database
            result.test_result = json.dumps(result_data, ensure_ascii=False)
            result.is_graded = True
            result.manual_score = new_score
            result.graded_at = datetime.now()
            result.graded_by = current_user.username
            
            db.session.commit()
            
            flash('Результат теста успешно проверен!', 'success')
            return redirect(url_for('creating_tests.test_results', test_id=test.id))
            
        except Exception as e:
            flash(f'Ошибка при сохранении оценок: {str(e)}', 'danger')
            print(traceback.format_exc())
    
    return render_template('creating_tests/grade_result.html',
                          result_id=result_id,
                          test_name=test_info.get('name', 'Без названия'),
                          student=student,
                          result=result_data)

