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
  #  available_tests = Test.query.filter(test_groups=form.username.data).first()
    print(current_user.group)
    return "Hello world"
