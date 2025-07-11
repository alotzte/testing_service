var blockCount = 0;
var questionBlocks = [];

var main_container = document.getElementById('main_container');

function autoResize(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = (textarea.scrollHeight) + 'px';
}

function updatePlaceholders(block) {
  const blockIndex = questionBlocks.indexOf(block.id) + 1;

  const question = block.querySelector('.question');
  question.placeholder = "Вопрос " + blockIndex;

  const answers = block.querySelectorAll('.answer input[type="text"]');
  answers.forEach((answer, index) => {
    answer.placeholder = "Вариант " + (index + 1);
  });
}

function updateDeleteButtons() {
  const questionDeleteButtons = document.querySelectorAll('.deleteQuestion');
  if (questionBlocks.length <= 1) {
    questionDeleteButtons.forEach(btn => btn.classList.add('hidden'));
  } else {
    questionDeleteButtons.forEach(btn => btn.classList.remove('hidden'));
  }

  document.querySelectorAll('.block').forEach(block => {
    const answerDeleteButtons = block.querySelectorAll('.deleteButton');
    const answersCount = block.querySelectorAll('.answer').length;

    answerDeleteButtons.forEach(btn => {
      if (answersCount <= 1) {
        btn.classList.add('hidden');
      } else {
        btn.classList.remove('hidden');
      }
    });
  });
}

function createQuestion() {
  blockCount++;
  var block = document.createElement('div');
  block.className = "block";
  block.id = "block" + blockCount;
  questionBlocks.push(block.id);

  var form = document.createElement('div');
  form.className = "form";

  var question = document.createElement('textarea');
  question.className = "question";
  question.addEventListener('input', function() {
    autoResize(this);
  });

  var plusButton = document.createElement('button');
  plusButton.className = "plusButton";
  plusButton.textContent = "Добавить ответ";
  plusButton.onclick = function() {
    createAnswer(form, block);
  };

  var deleteQuestion = document.createElement('button');
  deleteQuestion.className = 'deleteQuestion';
  deleteQuestion.textContent = "Удалить вопрос";
  deleteQuestion.onclick = function() {

    const index = questionBlocks.indexOf(block.id);
    if (index > -1) {
      questionBlocks.splice(index, 1);
    }
    main_container.removeChild(block);

    renumberBlocks();

    updateDeleteButtons();
  };

  var footbar = document.createElement('div');
  footbar.className = 'footbar';
  footbar.appendChild(plusButton);
  footbar.appendChild(deleteQuestion);

  form.appendChild(question);
  block.appendChild(form);
  block.appendChild(footbar);

  main_container.appendChild(block);
  autoResize(question);
  createAnswer(form, block);

  updatePlaceholders(block);

  updateDeleteButtons();
}

function createAnswer(form, block) {
  var answer = document.createElement('div');
  answer.className = 'answer';

  var select = document.createElement('input');
  select.type = 'radio';
  select.name = 'correctAnswer' + block.id.replace('block', '');
  select.className = 'select';

  var newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.className = 'newInput';

  var deleteButton = document.createElement('button');
  deleteButton.className = "deleteButton";
  deleteButton.textContent = "×";
  deleteButton.onclick = function() {
    form.removeChild(answer);

    updatePlaceholders(block);

    updateDeleteButtons();
  };

  answer.appendChild(select);
  answer.appendChild(newInput);
  answer.appendChild(deleteButton);

  form.appendChild(answer);


  updatePlaceholders(block);

  updateDeleteButtons();
}

function renumberBlocks() {

  const blocks = main_container.querySelectorAll('.block');
  questionBlocks = [];

  blocks.forEach((block, index) => {
    const newId = 'block' + (index + 1);
    block.id = newId;
    questionBlocks.push(newId);

    updatePlaceholders(block);

    const radios = block.querySelectorAll('input[type="radio"]');
    radios.forEach(radio => {
      radio.name = 'correctAnswer' + (index + 1);
    });
  });

  blockCount = blocks.length;

  updateDeleteButtons();
}


createQuestion();
