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

// Add event listener to save button
document.addEventListener('DOMContentLoaded', function() {
  const saveButton = document.getElementById('save-test');
  if (saveButton) {
    saveButton.addEventListener('click', function() {
      try {
        // Collect all test data
        const testData = {
          name: document.getElementById('testName').value,
          questions: []
        };
        
        // Get all question blocks
        const blocks = document.querySelectorAll('.block');
        blocks.forEach((block, blockIndex) => {
          const questionText = block.querySelector('.question').value || '';
          const answers = [];
          const answerInputs = block.querySelectorAll('.answer');
          
          let correctAnswerIndex = -1;
          
          answerInputs.forEach((answerInput, index) => {
            const answerText = answerInput.querySelector('input[type="text"]').value || '';
            const isSelected = answerInput.querySelector('input[type="radio"]').checked;
            
            answers.push({
              text: answerText,
              isCorrect: isSelected
            });
            
            if (isSelected) {
              correctAnswerIndex = index;
            }
          });
          
          testData.questions.push({
            question: questionText,
            answers: answers,
            correctAnswerIndex: correctAnswerIndex
          });
        });
        
        // Проверка на пустые значения
        if (!testData.name) {
          testData.name = "Новый тест";
        }
        
        // Проверка данных перед отправкой
        const jsonString = JSON.stringify(testData);
        console.log("JSON to send:", jsonString);
        
        // Send data to server
        fetch('/creator', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: jsonString
        })
        .then(response => {
          console.log("Response status:", response.status);
          return response.json();
        })
        .then(data => {
          console.log("Response data:", data);
          if (data.success) {
            alert('Тест успешно сохранен!');
            window.location.href = '/admin/dashboard';
          } else {
            alert('Произошла ошибка при сохранении теста: ' + data.message);
          }
        })
        .catch(error => {
          console.error('Error:', error);
          alert('Произошла ошибка при сохранении теста: ' + error);
        });
      } catch (error) {
        console.error("Error preparing data:", error);
        alert('Ошибка при подготовке данных: ' + error.message);
      }
    });
  }
});

// Create the first question when the page loads
createQuestion();
