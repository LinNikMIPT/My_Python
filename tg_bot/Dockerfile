FROM python:3.7.9-stretch
ENV PYTHONUNBUFFERED=1
# установка нужных утилит в систему, nano нужен для работы с ботом внутри контейнера (текстовый редактор)
RUN apt-get update && apt-get install nano
# установка pipenv
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
# копирование всех важных файлов в рабочую директорию
# запуск pipenv
CMD ["python", "configure_and_run.py"]
ENTRYPOINT ["python", "app.py"]
COPY . /app