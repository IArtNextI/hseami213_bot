from config_commands import BotCommand

'''
Документация по Markdown2
https://core.telegram.org/bots/api#markdownv2-style
'''

BotMessage = {

    BotCommand.help: '\n'.join((
          '/' + BotCommand.help + '- отобразить это сообщение'
        , '/' + BotCommand.add + ' - начать добавление дедлайна'
        , '/' + BotCommand.get + ' - отобразить список текущих дедлайнов'
        , '/' + BotCommand.chatid + ' - отобразить id текущей беседы'
        , '/' + BotCommand.userid + ' - отобразить id пользователя'
        , '/' + BotCommand.delete + ' - начать удаление дедлайна'
        , '/' + BotCommand.change + ' - перенести дедлайн'
        , '/' + BotCommand.wiki + ' - отобразить список ссылок на вики'
        , '/' + BotCommand.marks + ' - отобразить список ссылок на таблицы с оценками'
        , '/' + BotCommand.mark_formulas + ' - отобразить список формул оценок'
        , '/' + BotCommand.recordings + ' - отобразить ссылку на записи'
        , '/' + BotCommand.oakbus + ' - ссылка на расписание автобусов Дубков'
        , '/' + BotCommand.subscribe + ' - подписаться'
        , '/' + BotCommand.unsubscribe + ' - отписаться'
        , '/' + BotCommand.all + ' - пингануть подписчиков'
        , '/' + BotCommand.subs + ' - узнать подписчиков'
    )),

    BotCommand.mark_formulas: '\n'.join((
          '*Предмет*'
        , 'Oитог = отчислен'
        , 'Если не отчислен, то как?·'
    )),

    BotCommand.wiki: '\n'.join((
          '[Wiki](http://wiki.cs.hse.ru/%D0%97%D0%B0%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0)'
      ,
    )),

    BotCommand.marks: '\n'.join((
          '[РС](https://www.youtube.com/watch?v=MVIBf3cnTf0)'
      ,
    )),

    BotCommand.recordings: '\n'.join((
          r'[Какой\-то Яндекс\.Диск с записями](https://disk.yandex.ru/d/hVWLMgTBxXHBUQ)'
        , r'[YouTube ФКН](https://www.youtube.com/@hse\-cs\-lectures)'
        , r'[Записи c 1 курса](https://docs.google.com/spreadsheets/d/1wdON8nhfAyfMtm5\-ZY7U6ZI2xYPnDkemU5Zh3ZGA58k/edit#gid=0)',
    )),

    BotCommand.oakbus: '[Расписание](https://t.me/dubki/898)',

    BotCommand.subscribe: 'Ты в списке',

    BotCommand.unsubscribe: 'Вычеркнул тебя из списка',

    BotCommand.chatid: lambda message: message.chat.id,

    BotCommand.userid: lambda message: message.from_user.id,
}
