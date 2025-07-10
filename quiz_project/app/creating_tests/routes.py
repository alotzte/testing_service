from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from ..forms import RegistrationForm, LoginForm, TestCreatorForm, QuestionForm, CreateTestForm
from ..models import User, Test
from .. import db
import json
creating_tests_bp = Blueprint('creating_tests', __name__, template_folder='templates')

@creating_tests_bp.route('/creator', methods=['GET', 'POST'])
def create_test():
  if request.is_json:
    received_data = request.get_json()
    if received_data:
      json_string_to_store = json.dumps(received_data, indent=2, ensure_ascii=False)
      new_submission = Test(test_info=json_string_to_store)
      db.session.add(new_submission)
      db.session.commit()
      return "Vse Kruto, redirect kuda nibud please"
  return render_template('creating_tests/index.html')

