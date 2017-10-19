import time
import re
import vk as vk_api
import json

#   чтение конфигов и словаря
def collect_settings():
    config_file = open("config.json", "r")
    config = json.loads(config_file.read())
    config_file.close()

    dict_file = open(config['dict_path'], "r")
    dictionary = json.loads(dict_file.read())
    dict_file.close()

#   авторизация бота при помощи токена
bot = vk_api.VkApi(token = config['access_token'])

#   написать сообщение в чат или в лс
def write_msg(userID, chatID, msg):
    if chatID:
        bot.method('messages.send', {'chat_id': chatID,'message': msg})
    else:
        bot.method('messages.send', {'user_id': userID,'message': msg})

#   проверка функции на ключевые слова
def check_user_msg(funcDict, msg):
    msgDict = re.split('\W+', msg)
    for i in msgDict:
        if i in funcDict:
            return True
    return False

#   приветствие пользователя
def send_greeting(userID, chatID, msg):
    userInfo = bot.method('users.get', {'user_ids': userID})
    botGreeting = userInfo[0]['first_name'] + ', ку!\nЯ Костин бот-помощник)'
    write_msg(userID, chatID, botGreeting)

#   отправка времени
def send_time(userID, chatID, msg):
    botTime = time.ctime()
    write_msg(userID, chatID, botTime)

#  списки и словари
values = {'out': 0,'count': 200,'time_offset': 10}
sendGreetingDict = {'привет', 'ку'}
sendTimeDict = {'время', 'времени'}
functions = {send_greeting: sendGreetingDict, send_time: sendTimeDict}

#   основная часть
while True:
    response = bot.method('messages.get', values)
    if response['items']:
        values['last_message_id'] = response['items'][0]['id']

    for item in response['items']:
        userMsg = item['body'].lower()
        for func in functions:
            if check_user_msg(functions[func], userMsg):
                func(item['user_id'], item.get('chat_id', 0), userMsg)

    time.sleep(1)
