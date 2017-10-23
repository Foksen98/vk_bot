import time
import re
import vk_api
import json
import random
import xml.dom.minidom
import requests

#   чтение конфигов
def collect_settings():
    config_file = open("config.json", "r")
    config = json.loads(config_file.read())
    config_file.close()
    return config

#   инициализация словаря
def init_dictionary():
    dict_file = open(config['dict_path'], "r", encoding="utf8")
    dictionary = json.loads(dict_file.read())
    dict_file.close()
    return dictionary

config = collect_settings()
#   авторизация бота при помощи токена
bot = vk_api.VkApi(token = config['access_token'])
dictionary = init_dictionary()

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

#   выбор ответа из словаря
def give_answer(request):
    section = get_section(request = request)
    if section == "wolfram":
        answer = interact_with_wolfram(request[12:], config['wolfram_app_id'])
    # answer = random.choice(self.dict['sections']['hate']['answers'])
    else:
        answer = random.choice(dictionary['sections'][section]['answers'])
    return answer

#   определение группы вопроса
def get_section(request):
    request = request.lower()
    section_found = 'default'
    for section in dictionary['sections'].keys():
        for question in dictionary['sections'][section]['questions']:
            if re.findall(r'{}'.format(question), request):
                section_found = section
                break
    return section_found

def interact_with_wolfram(query, app_id):
    request = "http://api.wolframalpha.com/v2/query?input={}&appid={}".format(query, app_id)
    response = requests.get(request)
    dom = xml.dom.minidom.parseString(response.content);
    dom.normalize()
    try:
        node = dom.getElementsByTagName("img")[2]
        value = node.getAttribute("title")
    except:
        value = "Ой, что-то не работает, сорян!"    
    return value

#  списки и словари
values = {'out': 0,'count': 200,'time_offset': 10}
sendGreetingDict = {'привет', 'ку'}
sendTimeDict = {'время', 'времени'}
functions = {send_greeting: sendGreetingDict, send_time: sendTimeDict}

#  основная часть
while True:
    response = bot.method('messages.get', values)
    if response['items']:
        values['last_message_id'] = response['items'][0]['id']

    for item in response['items']:
        userMsg = item['body'].lower()
        # for func in functions:
        #     if check_user_msg(functions[func], userMsg):
        #         func(item['user_id'], item.get('chat_id', 0), userMsg)
        answer = give_answer(userMsg)
        write_msg(item['user_id'], item.get('chat_id', 0), answer)
    time.sleep(1)
