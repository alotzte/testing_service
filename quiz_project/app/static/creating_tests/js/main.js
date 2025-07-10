var blockCount=0;
var numAnswers=[];

var main_container = document.getElementById('main_container');
var main_button = document.getElementById('main_button');

function createQuestion(){
  var block = document.createElement('div');
  block.className = "block";

  var form = document.createElement('div');
  form.className = "form";

  block.appendChild(form);

  var question = document.createElement('input');
  question.type = "text";
  question.class = "question";
  question.placeholder = "Введите вопрос";

  var plusButton = document.createElement('button');
  plusButton.className = "plusButton";
  plusButton.textContent="Добавить ответ";
  plusButton.onclick = function() {
    createAnswer(form);
  }

  form.appendChild(question);
  block.appendChild(form);
  block.appendChild(plusButton);

  main_container.appendChild(block);
}

function createAnswer(form) {
  var answer = document.createElement('div');

  var newInput=document.createElement('input');
  newInput.type='text';

  deleteButton=document.createElement('button');
  deleteButton.className = "deleteButton";
  deleteButton.textContent="Delete";
  deleteButton.onclick = function() {
    form.removeChild(answer);
  };

  answer.appendChild(newInput);
  answer.appendChild(deleteButton);

  form.appendChild(answer);
}


createQuestion();
