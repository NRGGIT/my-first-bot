import random

import requests
import vk_api
from config import *


def write_msg(user_id, text):
    vk_bot.method('messages.send', {'user_id': user_id, 'message': text, 'random_id': random.randint(0, 1000)})


def write_msg_attach(user_id, text, att_url):
    vk_bot.method('messages.send',
                  {'user_id': user_id,
                   'attachment': att_url,
                   'message': text,
                   'random_id': random.randint(0, 1000)})


def get_last_post(owner_id, count, offset, filter): # пишем новую функцию на основе метода wall.get
    response = vk_bot_user.method('wall.get',
                                  {'owner_id': owner_id,
                                   'count': count,
                                   'offset': offset,  # offset = 1, в случае, если есть закрепленный пост
                                   'filter': filter}) # т.к. он не самый свежий,
                                                      # потому используем сдвиг на один пост
    return response['items'][0]['id'] # все, что нам нужно от этого метода - id поста,
                                      # return возвращает полученное значение


vk_bot_user = vk_api.VkApi(token=ACCOUNT_TOKEN) #wall.get только для юзеров,
                                                # потому нужна отдельная авторизация

vk_bot = vk_api.VkApi(token=ACCESS_TOKEN)
long_poll = vk_bot.method('messages.getLongPollServer', {'need_pts': 1, 'lp_version': 3})
server, key, ts = long_poll['server'], long_poll['key'], long_poll['ts']
print("готов к работе")

while True:
    long_poll = requests.get(
        'https://{server}?act={act}&key={key}&ts={ts}&wait=500'.format(server=server,
                                                                       act='a_check',
                                                                       key=key,
                                                                       ts=ts)).json()

    update = long_poll['updates']
    if update[0][0] == 4:
        print(update)
        user_id = update[0][3]
        user_name = vk_bot.method('users.get', {'user_ids': user_id})
        write_msg(user_id, 'Привет, ' + (user_name[0]['first_name']))

        if 'картинк' in update[0][6]:
            write_msg_attach(user_id,
                             'вот тебе огненная картинка',
                             'photo-171720905_456239025')

        if 'красив' in update[0][6]: #ищет набор букв "красив" в сообщении
            group_id = -35684707 #id групп всегда начинается с минуса
            post_id = get_last_post(group_id, 1, 1, 'owner')
            attach = 'wall' + str(group_id) + '_' + str(post_id) #формируем ссылку на пост
            write_msg_attach(user_id, 'вот тебе красота', attach)

        print(str(user_name[0]['first_name']) + ' ' +
              str(user_name[0]['last_name']) + ' написал(а) боту - ' + str(update[0][6]))
    ts = long_poll['ts']
