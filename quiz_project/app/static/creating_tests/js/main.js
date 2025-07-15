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
  
  // Для текстового ответа
  const textAnswer = block.querySelector('.text-answer textarea');
  if (textAnswer) {
    textAnswer.placeholder = "Введите правильный ответ";
  }
}

function updateDeleteButtons() {
  const questionDeleteButtons = document.querySelectorAll('.deleteQuestion');
  if (questionBlocks.length <= 1) {
    questionDeleteButtons.forEach(btn => btn.classList.add('hidden'));
  } else {
    questionDeleteButtons.forEach(btn => btn.classList.remove('hidden'));
  }

  document.querySelectorAll('.block').forEach(block => {
    // Только для вопросов с вариантами ответов
    if (block.querySelector('.question-type-select').value === 'multiple_choice') {
      const answerDeleteButtons = block.querySelectorAll('.deleteButton');
      const answersCount = block.querySelectorAll('.answer').length;

      answerDeleteButtons.forEach(btn => {
        if (answersCount <= 2) {
          btn.classList.add('hidden');
        } else {
          btn.classList.remove('hidden');
        }
      });
    }
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
  

  // Создаем контейнер для ответов
  var answersContainer = document.createElement('div');
  answersContainer.className = "answers-container";
  
  // Создаем контейнер для текстового ответа
  var textAnswerContainer = document.createElement('div');
  textAnswerContainer.className = "text-answer";
  textAnswerContainer.style.display = "none";
  
  var textAnswerArea = document.createElement('textarea');
  textAnswerArea.className = "text-answer-area";
  textAnswerArea.addEventListener('input', function() {
    autoResize(this);
  });
  textAnswerArea.placeholder = "Место для развернутого ответа";
  textAnswerArea.rows = 5;
  
  textAnswerContainer.appendChild(textAnswerArea);
  
  // Создаем кнопку добавления ответа
  var plusButtonContainer = document.createElement('div');
  plusButtonContainer.className = "plusButtonContainer";

  var plusButton = document.createElement('button');
  plusButton.className = "plusButton";
  plusButton.textContent = "Добавить ответ";
  plusButton.onclick = function() {
    createAnswer(answersContainer, block);
  };
  plusButtonContainer.appendChild(plusButton);
  
  // Создаем кнопку удаления вопроса
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

  var typeSelect = document.createElement('select');
  typeSelect.className = "question-type-select";

  var optionMultipleChoice = document.createElement('option');
  optionMultipleChoice.value = "multiple_choice";
  optionMultipleChoice.textContent = "С выбором ответа";

  var optionTextAnswer = document.createElement('option');
  optionTextAnswer.value = "text_answer";
  optionTextAnswer.textContent = "С развернутым ответом";

  typeSelect.appendChild(optionMultipleChoice);
  typeSelect.appendChild(optionTextAnswer);

  var footbar = document.createElement('div');
  footbar.className = 'footbar';
  footbar.appendChild(plusButtonContainer);
  footbar.appendChild(typeSelect);
  footbar.appendChild(deleteQuestion);


  // Обработчик изменения типа вопроса
  typeSelect.addEventListener('change', function() {
    if (this.value === 'multiple_choice') {
      answersContainer.style.display = "block";
      textAnswerContainer.style.display = "none";
      plusButton.style.display = "inline-block"; // Показываем кнопку "Добавить ответ"
      
      // Если нет вариантов ответа, добавляем два
      if (answersContainer.querySelectorAll('.answer').length === 0) {
        createAnswer(answersContainer, block);
        createAnswer(answersContainer, block);
      }
    } else {
      answersContainer.style.display = "none";
      textAnswerContainer.style.display = "block";
      plusButton.style.display = "none"; // Скрываем кнопку "Добавить ответ"
    }
  });

  form.appendChild(question);
  form.appendChild(answersContainer);
  form.appendChild(textAnswerContainer);
  
  block.appendChild(form);
  block.appendChild(footbar);

  main_container.appendChild(block);
  autoResize(question);
  
  // По умолчанию создаем два варианта ответа для вопроса с выбором
  createAnswer(answersContainer, block);
  createAnswer(answersContainer, block);

  updatePlaceholders(block);
  updateDeleteButtons();
}

function createAnswer(container, block) {
  var answer = document.createElement('div');
  answer.className = 'answer';

  var select = document.createElement('input');
  select.type = 'radio';
  select.name = 'correctAnswer' + block.id.replace('block', '');
  select.className = 'select';
  
  // Добавляем обработчик события для выделения правильного ответа
  select.addEventListener('change', function() {
    // Найти все текстовые поля в этом блоке
    const textInputs = block.querySelectorAll('.answer input[type="text"]');
    textInputs.forEach(input => {
      input.classList.remove('correct-answer');
    });
    
    // Выделить текстовое поле рядом с выбранной радиокнопкой
    if (this.checked) {
      const textInput = this.parentElement.querySelector('input[type="text"]');
      if (textInput) {
        textInput.classList.add('correct-answer');
      }
    }
  });

  var newInput = document.createElement('input');
  newInput.type = 'text';
  newInput.className = 'newInput';

  var deleteButton = document.createElement('button');
  deleteButton.className = "deleteButton";
  deleteButton.textContent = "×";
  deleteButton.onclick = function() {
    container.removeChild(answer);
    updatePlaceholders(block);
    updateDeleteButtons();
  };

  answer.appendChild(select);
  answer.appendChild(newInput);
  answer.appendChild(deleteButton);

  container.appendChild(answer);

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

// Функция валидации теста
function validateTest() {
  const blocks = document.querySelectorAll('.block');
  
  // Проверка названия теста
  const testName = document.getElementById('testName').value.trim();
  if (!testName) {
    return { isValid: false, errorMessage: 'Название теста не может быть пустым' };
  }
  
  // Проверка наличия вопросов
  if (blocks.length === 0) {
    return { isValid: false, errorMessage: 'Тест должен содержать хотя бы один вопрос' };
  }
  
  // Проверка вопросов и ответов
  for (let i = 0; i < blocks.length; i++) {
    const block = blocks[i];
    const questionText = block.querySelector('.question').value.trim();
    const questionType = block.querySelector('.question-type-select').value;
    
    // Проверка текста вопроса
    if (!questionText) {
      return { isValid: false, errorMessage: `Вопрос ${i + 1} не может быть пустым` };
    }
    
    // Проверки в зависимости от типа вопроса
    if (questionType === 'multiple_choice') {
      const answers = block.querySelectorAll('.answer');
      
      // Проверка количества ответов
      if (answers.length < 2) {
        return { isValid: false, errorMessage: `Вопрос ${i + 1} должен иметь как минимум 2 варианта ответа` };
      }
      
      // Проверка текста ответов и наличия выбранного правильного ответа
      let hasCorrectAnswer = false;
      for (let j = 0; j < answers.length; j++) {
        const answer = answers[j];
        const answerText = answer.querySelector('input[type="text"]').value.trim();
        
        // Проверка текста ответа
        if (!answerText) {
          return { isValid: false, errorMessage: `Ответ ${j + 1} в вопросе ${i + 1} не может быть пустым` };
        }
        
        // Проверка наличия правильного ответа
        if (answer.querySelector('input[type="radio"]').checked) {
          hasCorrectAnswer = true;
        }
      }
      
      if (!hasCorrectAnswer) {
        return { isValid: false, errorMessage: `Для вопроса ${i + 1} не выбран правильный ответ` };
      }
    }
  }
  
  return { isValid: true, errorMessage: '' };
}

function addGroupField() {
  const groupContainer = document.getElementById("groupContainer");
  const newGroupField = document.createElement("div");
  newGroupField.className = "groupField";
  newGroupField.innerHTML = `
    <input type="text" class="groupInput" name="groups[]">
  `;

  groupContainer.appendChild(newGroupField);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
  // Создаем первый вопрос, если его еще нет
  if (!document.querySelector('.block')) {
    createQuestion();
  }
  
  // Добавляем обработчик для кнопки сохранения теста
  const saveButton = document.getElementById('custom-save-btn');
  if (saveButton) {
    saveButton.addEventListener('click', function(e) {
      // Предотвращаем стандартное поведение кнопки
      e.preventDefault();
      e.stopPropagation();
      
      // Валидация теста перед отправкой
      const validation = validateTest();
      const validationMessage = document.getElementById("validation-message");
      
      if (!validation.isValid) {
        // Показываем сообщение об ошибке
        if (validationMessage) {
          validationMessage.textContent = validation.errorMessage;
          validationMessage.classList.add('show');
        }

        // Прерываем выполнение функции
        return;
      }
      
      // Если валидация пройдена, скрываем сообщение об ошибке
      if (validationMessage) {
        validationMessage.classList.remove('show');
      }
      
      // Собираем данные теста
      const testData = {
        name: document.getElementById('testName').value,
        questions: [],
        groups: []  // Инициализируем массив groups
      };

      // Получаем значения из полей групп
      const groupInputs = document.querySelectorAll(".groupInput");
      const groups = Array.from(groupInputs).map(input => input.value);
      testData.groups = groups;  // Добавляем массив groups в testData
      
      // Получаем все блоки вопросов
      const blocks = document.querySelectorAll('.block');
      blocks.forEach((block, blockIndex) => {
        const questionText = block.querySelector('.question').value;
        const questionType = block.querySelector('.question-type-select').value;
        
        // Создаем объект вопроса с общими свойствами
        const questionObj = {
          question: questionText,
          type: questionType
        };
        
        if (questionType === 'multiple_choice') {
          // Для вопроса с вариантами ответов
          const answers = [];
          const answerInputs = block.querySelectorAll('.answer');
          
          let correctAnswerIndex = -1;
          
          answerInputs.forEach((answerInput, index) => {
            const answerText = answerInput.querySelector('input[type="text"]').value;
            const isSelected = answerInput.querySelector('input[type="radio"]').checked;
            
            answers.push({
              text: answerText,
              isCorrect: isSelected
            });
            
            if (isSelected) {
              correctAnswerIndex = index;
            }
          });
          
          questionObj.answers = answers;
          questionObj.correctAnswerIndex = correctAnswerIndex;
        } else {
          // Для вопроса с текстовым ответом
          questionObj.textAnswer = block.querySelector('.text-answer textarea').value || '';
        }
        
        testData.questions.push(questionObj);
      });
      
      // Отправляем данные на сервер только если валидация пройдена
      fetch('/creator', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          window.location.href = "/my-tests";
        } else {
          alert('Произошла ошибка при сохранении теста: ' + data.message);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка при сохранении теста');
      });
    });
  }
  
  // Проверяем все блоки вопросов и скрываем кнопку "Добавить ответ" для вопросов с развернутым ответом
  document.querySelectorAll('.block').forEach(block => {
    const typeSelect = block.querySelector('.question-type-select');
    const plusButton = block.querySelector('.plusButton');
    
    if (typeSelect && plusButton && typeSelect.value === 'text_answer') {
      plusButton.style.display = 'none';
    }
  });
});
