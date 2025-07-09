from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from ..forms import RegistrationForm, LoginForm, TestCreatorForm, QuestionForm
from ..models import User, Test
from .. import db

creating_tests_bp = Blueprint('creating_tests', __name__, template_folder='templates')

@creating_tests_bp.route('/creator', methods=['GET', 'POST'])
def create_test():
  form = TestCreatorForm()
  print(request.form)

#  print(form.add_question)
 # return "Hello world"
 # if form.add_question.data():
 #   form.questions_list.append_entry()
 #   return render_template('creating.html', form=form)
  return render_template('creating_tests/creating_tests.html', form=form)
 # if form.submit_test.data and form.validate():
''' g
      test_data = {
          'title': form.title_of_test.data,
          'questions': [
              {
                  'text': q.text.data,
                  'answers': [
                      {'text': a.text.data, 'is_correct': a.is_correct.data}
                      for a in q.answers_list
                  ]
              }
              for q in form.questions_list
          ]
      }
      return redirect(url_for('success'))
'''
  
#  return "Hello world"

