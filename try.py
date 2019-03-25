
shop = {'яблоки': 18, #так в питоне записываются словари
        'бананы': 20,
        'груши': 40}

while True:
    response = input('Введите название, чтобы узнать количество: ')
    try:
        print(shop[response])

    except KeyError:
        print('У нас такого нет')