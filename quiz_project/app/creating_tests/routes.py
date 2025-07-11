from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps

from ..models import User, Test
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
    
    if request.method == 'POST':
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
                        test_info=json_string_to_store
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

