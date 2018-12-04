import simplejson as json
import requests, time
from config import *

#коммент для проверки git
value = 'переменная для проверки git'


MASTER_ID = 2299551
sent_posts_history_dict = {}
lp_update_time = time.time()

def message_interpreter(text, word_topic_dic, topic_group_dic): #нужна для того, чтобы распознавать слова по корням (пример: скинь котейку. видит, находит "кот" в word_topic_dic и его значение находит в GroupsDic, где получает id нужной группы)
	text = text.lower()
	for key in word_topic_dic.keys():
		if key in text:
			groupKey = (word_topic_dic[key])
			return int(topic_group_dic[groupKey])
			break
	return 'interp error'


def sent_posts_history(udic, n, m): #ведение любого учета, например постов показанных пользователю (lists in dicts)
	if n in udic.keys():
		udic[n].append(m)
	else:
		udic[n] = []
		udic[n].append(m)
	return udic

def find_best_fresh_post(owner_id, user): #поиск лучшего поста в заданной группе за последние сутки. сохраняет id поста в IDHistory для данного пользователя, чтобы потом не скидывать тот же пост при таком же запросе.
	posts = json.loads((requests.get('https://api.vk.com/method/wall.get?owner_id={owner_id}&count={count}&filter={filter}&access_token={token}&v={version}'.format(owner_id = owner_id,
																														   	   		   						 count = 40,
																														   	   		   						 filter = 'all',
																														               						 token = ACCAUNT_TOKEN,
																														       	       						 version = '5.80'))).text)['response']
	likes_posts_dict = {}
	for post in posts['items']:
		ID = post['id']
		likes_count = post['likes']['count']
		try:
			if (time.time() - post['date']) < 86400 and ID not in sent_posts_history_dict[user]:
				likes_posts_dict[likes_count] = ID
		except KeyError:
			likes_posts_dict[likes_count] = ID
	if len(likes_posts_dict) == 0:
		return 'thats all'
	else:
		best = likes_posts_dict[max(likes_posts_dict.keys())]
		sent_posts_history(sent_posts_history_dict, user, best)
		return best

def write_msg(user_id, text):
    requests.get('https://api.vk.com/method/messages.send?user_id={id}&message={text}&access_token={token}&v={version}'.format(id = user_id,
																														   	   text = text,
																														       token = GROUP_TOKEN,
																														       version = '5.80'))

def send_post(user_id, text, attach):
	requests.get('https://api.vk.com/method/messages.send?user_id={id}&message={text}&attachment={attach}&access_token={token}&v={version}'.format(id = user_id,
																																				   text = text,
																																				   attach = attach,
																																	 			   token = GROUP_TOKEN,
																																	 			   version = '5.80'))
def lp_update():
    return json.loads((requests.get('https://api.vk.com/method/messages.getLongPollServer?need_pts={need_pts}&lp_version={lp_version}&access_token={token}&v={version}'.format(need_pts = 1,
																																								               lp_version = 3,
																																								               token = GROUP_TOKEN,
																																								               version = '5.80'))).text)['response']
lp_server = lp_update()
write_msg(MASTER_ID, ('Бот включен'))

while True:
	if (time.time() - lp_update_time) >= 3480: #every 58 minutes lp_server needs to update
	    lp_update_time = time.time()
	    lp_server = lp_update()

	response = json.loads((requests.get('https://{server}?act=a_check&key={key}&ts={ts}&wait=20ms&mode=2&version=3'.format(server = lp_server['server'],
																											               key = lp_server['key'],
																											               ts = lp_server['ts']))).text)
	try:
	    updates = response['updates']
	except KeyError:
	    write_msg(mess_id, ('Ошибка KeyError -updates-'))
	    write_msg(mess_id, (str(response)))
	    updates = []
	    lp_server = lp_update()
	    response['ts'] = lp_server['ts']
	if updates:
		if updates[0][0] == 4 and (updates[0][2] == 17 or updates[0][2] == 1): #4 - новое сообщение, 17 - сообщение мне, с телефона 1 -
			text = updates[0][5].lower()
			print('new massage')
			mess_id = updates[0][3]
			owner_id = message_interpreter(text, WORD_TO_TOPIC, TOPIC_TO_GROUP)

			if 'привет' in text: #далее всякие команды можно добавлять, чтобы управлять им из чата
				topics = ''
				for key in TOPIC_TO_GROUP.keys():
					topics += ', ' + str(key)
				write_msg(mess_id, 'Привет, я Marvin. Я могу тебе прислать лучшие посты групп по темам:' + topics[1:] + '. Просто попроси, например, так: "скинь мне научный пост"')
			elif text == MARVIN:
				write_msg(mess_id, 'Я так и знал, что к этому все приведет. Выключаюсь...')
				break
			elif 'updates' in text:
			    write_msg(mess_id, response)
			elif owner_id == 'interp error':
				write_msg(mess_id, 'такого я не знаю(')
			else:
				best_post_id = find_best_fresh_post(owner_id, mess_id)
				if best_post_id == 'thats all':
					write_msg(mess_id, 'по этому запросу пока все')
				else:
					wallpost = 'wall' + str(owner_id) + '_' + str(best_post_id)
					send_post(mess_id, 'вот', wallpost)
	lp_server['ts'] = response['ts']
write_msg(MASTER_ID, 'Бот выключен') #это работает только, если выключение по команде Marvin