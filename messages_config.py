from commands_config import bot_command

'''
Документация по Markdown2
https://core.telegram.org/bots/api#markdownv2-style
'''

def get_formated_todays_schedule(todays_schedule):
    res = '~~~~~~~~~\n'
    for lesson in todays_schedule:
        res += '\n'.join((
            ''
            , lesson['kindOfWork'] + ': ' + lesson['discipline'].replace(" (рус)", '')
            , 'Аудитория: ' + lesson['auditorium']
            , 'Начало: ' + lesson['beginLesson']
            , 'Конец: ' + lesson['endLesson']
            , ''
            , '~~~~~~~~~'
            , ''
        ))
    return res

bot_message = {

    bot_command.help: '\n'.join((
          '/' + bot_command.help + '- отобразить это сообщение'
        , '/' + bot_command.add + '- начать добавление дедлайна'
        , '/' + bot_command.get + '- отобразить список текущих дедлайнов'
        , '/' + bot_command.today + '- отобразить рассписание на сегодня'
        , '/' + bot_command.chatid + '- отобразить id текущей беседы'
        , '/' + bot_command.userid + '- отобразить id пользователя'
        , '/' + bot_command.delete + '- начать удаление дедлайна'
        , '/' + bot_command.wiki + '- отобразить список ссылок на вики'
        , '/' + bot_command.marks + '- отобразить список ссылок на таблицы с оценками'
        , '/' + bot_command.linal + '- отобразить ссылки на Yandex.Disk с дз по линалу и на задачник Кострикина'
        , '/' + bot_command.mark_formulas + '- отобразить список формул оценок'
        , '/' + bot_command.recordings + ' - отобразить ссылку на записи'
        , '/' + bot_command.oakbus + ' - ссылка на расписание автобусов Дубков'
        , '/' + bot_command.subscribe + ' - подписаться'
        , '/' + bot_command.unsubscribe + ' - отписаться'
        , '/' + bot_command.all + ' - пингануть подписчиков'
        , '/' + bot_command.subs + ' - узнать подписчиков'
    )),

    bot_command.mark_formulas: '\n'.join((
          '*ТВиМС (пилот)*'
        , 'Oитог = 0.25 · Окр + 0.3 · Околлоквиум + 0.15 · Одз + 0.3 · Оэкзамен'
        , 'Если округленная накопленная оценка получается 8 и выше, то можно получить автомат и зачесть ее как итоговую.'
        , '*ТВиМС (основа)*'
        , 'О = 0.3(Кр1 + Кр2) + 0.15(Кл1 + Кл2) + 0.1Дз.'
        , '*Матан - 2*'
        , 'Oосень = 1/6 · (ДЗ + КЛ1+ КЛ2 ) + 1/4 · (КР1 + КР2)'
        , '*Advanced C++*'
        , 'Oитоговая = min(10; 0,6 · OБольшие ДЗ + 0,4 · OРегулярные ДЗ + 0,1 · OЕженедельные квизы + 0,1 · OБонусные задачи).'
        , '*Математическая логика*'
        , 'Р = ОКРУГЛ ( min (10, 0.35 · ЭКЗ + 0.35 · КОЛ + 3 · ДЗ) )'
        , '*Advanced Python*'
        , '0,1 · ДЗ1 + 0,1 · ДЗ2 + 0,15 · ДЗ3 + 0,15 · ДЗ4 + 0,5 · Проект'
        , '*Rust*'
        , 'Oитоговая = min(10; 0,5 · Oнедельные задачи + 0,5 · Oпроекты + доп.баллы), доп.баллов может быть не больше двух'
        , '*Алгосы*'
        , 'Оитог = 0.3 · Оконтесты (2 + 3 модуль) + 0.25 · Oлистки (2 + 3 модуль) + 0.15 · Oконтрольная + 0.3 · Oэкзамен + Oбонус'
        , 'Оконтесты = 10 · ((КК + ДК)/ (ОЗ - поправка) + БЗ / ОЗ), где:'
        , 'КК — баллы за короткие контесты'
        , 'ДК — баллы за длинные контесты (исключая бонусные задачи)'
        , 'БЗ — баллы за бонусные задачи в длинных контестах'
        , 'ОЗ — общее число задач во всех контестах (исключая бонусные задачи)'
        , 'Поправка по умолчанию равна нулю и может быть увеличена индивидуально для каждого студента при наличии пропусков по уважительным причинам.'
    )),

    bot_command.wiki: '\n'.join((
          '[Wiki](http://wiki.cs.hse.ru/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0)'
        , '[ТВиМС пилот](http://wiki.cs.hse.ru/%D0%A2%D0%B5%D0%BE%D1%80%D0%B8%D1%8F_%D0%B2%D0%B5%D1%80%D0%BE%D1%8F%D1%82%D0%BD%D0%BE%D1%81%D1%82%D0%B5%D0%B9_2022/2023_(%D0%BF%D0%B8%D0%BB%D0%BE%D1%82%D0%BD%D1%8B%D0%B9_%D0%BF%D0%BE%D1%82%D0%BE%D0%BA\))'
        , '[ТВиМС основа](http://wiki.cs.hse.ru/%D0%A2%D0%B5%D0%BE%D1%80%D0%B8%D1%8F_%D0%B2%D0%B5%D1%80%D0%BE%D1%8F%D1%82%D0%BD%D0%BE%D1%81%D1%82%D0%B5%D0%B9_2022/2023_(%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9_%D0%BF%D0%BE%D1%82%D0%BE%D0%BA\))'
        , '[Матан\-2](http://wiki.cs.hse.ru/%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9_%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D0%B7_-_2_(2022/23\))'
        , '[Advanced C\+\+](http://wiki.cs.hse.ru/%D0%AF%D0%B7%D1%8B%D0%BA_%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F_C%2B%2B_(%D1%83%D0%B3%D0%BB%D1%83%D0%B1%D0%BB%D0%B5%D0%BD%D0%BD%D1%8B%D0%B9_%D0%BA%D1%83%D1%80%D1%81\)_2022)'
        , '[Математическая логика](http://wiki.cs.hse.ru/%D0%9C%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B0%D1%8F_%D0%BB%D0%BE%D0%B3%D0%B8%D0%BA%D0%B0_%D0%9F%D0%9C%D0%98_22/23)'
        , '[Advanced Python](http://wiki.cs.hse.ru/%D0%9F%D1%80%D0%BE%D0%B4%D0%B2%D0%B8%D0%BD%D1%83%D1%82%D1%8B%D0%B9_Python_2022/2023)'
        , '[Алгосы *OUTDATED*](http://wiki.cs.hse.ru/%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC%D1%8B_%D0%B8_%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D1%8B_%D0%B4%D0%B0%D0%BD%D0%BD%D1%8B%D1%85_%D0%BF%D0%B8%D0%BB%D0%BE%D1%82%D0%BD%D1%8B%D0%B9_%D0%BF%D0%BE%D1%82%D0%BE%D0%BA_2021/2022)'
        , '[Rust](http://wiki.cs.hse.ru/%D0%AF%D0%B7%D1%8B%D0%BA_%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F_Rust)'
    )),

    bot_command.marks: '\n'.join((
          '*OUTDATED*'
        , '[Линал Семы](https://docs.google.com/spreadsheets/d/1Uoe6ThMa5R8Qij3xexE1reel5aDLue47iFVm6xous_w/edit#gid=0)'
        , '[Линал ИДЗ](https://docs.google.com/spreadsheets/d/1HBbgUG6nstuJVWAXn7uoGD7tZ2uQesK27YXKN04ZsrE/edit#gid=1697515667)'
        , '[Матан](https://docs.google.com/spreadsheets/d/1lkssP6PGxxfe15ffiPatcamoV9e-WOlq8ysUqIbuzTI/edit#gid=1488201705)'
        , '[Алгосы](https://docs.google.com/spreadsheets/d/1bRg_nUNZxfPY-JxFXvzAvPb-GwWZ8Cv8gxJSJgo-uhA/edit)'
        , '[Алгебра](https://docs.google.com/spreadsheets/d/1KfALsqsOcXeU4TDb9U2tQhRyJ0eaIDfCRRZK5Y9HK1g/edit#gid=1697515667)'
    )),

    bot_command.linal: '\n'.join((  
          '*OUTDATED*'
        , '[Линал ДЗ](https://disk.yandex.ru/d/idvfp8FiufvVLA)'
        , '[Линал Кострикин](https://disk.yandex.ru/i/ayIeELGipfO4_Q)'
    )),

    bot_command.recordings: '\n'.join((
          '*OUTDATED*'
        , '[Записи](https://docs.google.com/spreadsheets/d/1wdON8nhfAyfMtm5-ZY7U6ZI2xYPnDkemU5Zh3ZGA58k/edit#gid=0)',
    )),

    bot_command.oakbus: '[Расписание](https://t.me/c/1597210278/70153)',

    bot_command.subscribe: 'Ты в списке',

    bot_command.unsubscribe: 'Вычеркнул тебя из списка',

    bot_command.chatid: lambda message: message.chat.id,

    bot_command.userid: lambda message: message.from_user.id,

    bot_command.today: lambda todays_schedule: get_formated_todays_schedule(todays_schedule)
}
