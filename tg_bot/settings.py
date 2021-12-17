import requests

BOT_TOKEN = "12345"
URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'
FILE_URL = f'https://api.telegram.org/bot/file/{BOT_TOKEN}/'

# Эта функция достает фотографию из апи телеграма по ее id
def get_file(id):
    url = URL + 'getFile'
    file = {
        'file_id': id
    }
    response = requests.get(url, file)
    file_path = response.json()['result']['file_path']
    response2 = requests.get(f"https://api.telegram.org/file/bot1818108208:AAEkAfmt97tHAvT4TZgUv8f4aAOFNadrGzw/{file_path}")
    return response2.content
