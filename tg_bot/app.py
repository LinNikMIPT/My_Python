# requests - Библиотека для отправки запросов
import requests 
# Библиотека для работы с json файлами
import json
# стандартная библиотека python для логирования того что происходит с программой
import logging
import io
# Импорт класса Flask и request для перехвата запрососов
# на наш сервер flask
from flask import Flask
from flask import request
from flask import jsonify

from PIL import Image, ImageFilter

# Импортируем функцию serve для запуска wsgi сервера
from waitress import serve

# Импортируем токен бота
from settings import BOT_TOKEN, get_file
from configure_and_run import get_tunnel_url
# Инициализируем логгер файла чтобы отслеживать все происходящее
logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Плучаем tunnel url
tunnel_url = get_tunnel_url()

# Иницилизируем flask приложение для запуска серва
app = Flask(__name__)
# Готовим url для отправки запросов на api телеграма
URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'
file_url = "https://api.telegram.org/file/bot1818108208:AAEkAfmt97tHAvT4TZgUv8f4aAOFNadrGzw"

def set_webhook():
    url = URL + f'setWebhook?url={tunnel_url}'
    return requests.get(url)


# Записываем ответы от API телеграма в файл для удобства работы с ним
def write_json(data, filename='answer.json'):
    # Открываем файл answer.json
    with open(filename, 'w') as f:
        # Выгружаем туда json полученый из ответа
        json.dump(data, f, indent=2, ensure_ascii=False)

photos = {
    
}
# Отправляем сообщение пользователю по его chat_id взятому из get_updates
def send_message(chat_id, text='bla-bla-bla', photo_id=None, reply_markup=False):
    show_photo_button =json.dumps({
                    'inline_keyboard':[
                        [
                        {'text':'gaussin', 'callback_data': f"do_gaussian:{photo_id}"},
                        {'text':'grayscale', 'callback_data': f"make_grayscale:{photo_id}"}
                        ],
                    ]
                })
    url = URL + 'sendMessage'
    answer = {
        'chat_id': chat_id,
        'text': text,
    }
    if reply_markup == True:
        answer.update({'reply_markup': show_photo_button})
    response = requests.post(url, answer)
    print(response.json())

    return response.json()


def send_photo(chat_id, photo_id):
    url = URL + 'sendPhoto'
    answer = {
        'chat_id': chat_id,
        
    }
    files = {
        'photo': photo_id,
    }
    # headers = {
    #     "Content-Type": "multipart/form-data"
    # }
    response = requests.post(url, data=answer, files=files)
    print(response.json())

@app.route('/', methods=['POST', 'GET'])
def index():
    # Телеграм отправляет POST запросы на наш webhook сервер
    if request.method == 'POST':
        # Собираем json из пост запроса
        r = request.get_json()
        # смотрим кнопка ли это
        callback_query = r.get('callback_query')
        # Если кнопка
        if callback_query:
            # Берем id чата
            chat_id = callback_query['from']['id']
            # Парсим id фотографии
            callback_data = callback_query['data']
            # Проверяем верную ли кнопку нажали
            if callback_data.split(":")[0] == 'make_grayscale':
                # Обработка кнопки grayscale
                # Отпраляем фото по апросу
                # get_file достает фото из апи телеграма по его id в двоичном формате
                photo = get_file(photos[callback_data.split(":")[1]])
                # здесь создается обертка этого формата для возможности открытия
                photo = io.BytesIO(photo)
                photo = Image.open(photo)
                # конвертируем в черное-белый цвет
                photo = photo.convert('LA')
                byteIO = io.BytesIO()
                # тут сохраняем фото в переменную byteIO так как Image.open сделал из нее объект класса Image
                photo.save(byteIO, format='PNG')
                # Тут создаем обратно двоичный формат
                byteArr = byteIO.getvalue()
                # Отправляем фото
                send_photo(chat_id, byteArr)
            elif callback_data.split(":")[0] == 'do_gaussian':
                # Обработка кнопки gaussian
                # Отпраляем фото по апросу
                # get_file достает фото из апи телеграма по его id в двоичном формате
                photo = get_file(photos[callback_data.split(":")[1]])
                # здесь создается обертка этого формата для возможности открытия
                photo = io.BytesIO(photo)
                photo = Image.open(photo)
                # используем фильтр
                photo = photo.filter(ImageFilter.GaussianBlur(radius = 3))
                byteIO = io.BytesIO()
                # тут сохраняем фото в переменную byteIO так как Image.open сделал из нее объект класса Image
                photo.save(byteIO, format='PNG')
                # Тут создаем обратно двоичный формат
                byteArr = byteIO.getvalue()
                # Отправояем фото
                send_photo(chat_id, byteArr)
        else:
            # Если не кнопка а сообщение
            message = r.get('message')
            # Если текст
            if message.get('text'):
                # Бере id чата и возвращаем то же самое сообщение
                chat_id = r['message']['chat']['id']
                send_message(chat_id, message.get('text'))
            elif message.get('photo'):
                # Если фото также берем id но отпраляем фото
                chat_id = r['message']['chat']['id']
                # Мы не можем просто отправить id фото так как id слишком большой чтобы добавить его в callbackdata
                send_message(chat_id, 'Отправить фото',
                             photo_id=message['photo'][0]['file_unique_id'],
                             reply_markup=True)
                # Для этого мы берем короткую версию id и заносим в словарь чтобы позже к нему обратиться
                # и получить полное айди для отправки
                photos.update({message['photo'][0]['file_unique_id']: message['photo'][0]['file_id']})
            else:
                # Во всез остальных случаях просим отправить фото или текст
                chat_id = r['message']['chat']['id']
                send_message(chat_id, 'Отправьте текст или фотографию')
        write_json(r)
        return jsonify(r)
    return "<h1> Hello bot </h1>"


if __name__ == '__main__':
    set_webhook()
    # Запускаем сервер
    app.run()

