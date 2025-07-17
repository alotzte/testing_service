# Используем официальный образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
# Это делается отдельным шагом для использования кэша Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое папки quiz_project в рабочую директорию /app
COPY ./quiz_project/ .

# Указываем, что контейнер будет слушать порт 5000
EXPOSE 5000

# Устанавливаем переменные окружения для Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Команда для запуска приложения
# host=0.0.0.0 делает приложение доступным извне контейнера
CMD ["flask", "run", "--host=0.0.0.0"] 