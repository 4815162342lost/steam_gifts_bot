# steam gifts bot
Written on Python3.

Description
bot for http://www.steamgifts.com/ I use my program 1 month, all good, But if you account will be banned, i not will be guilty.

Requirements: python 3
Requirements modules for Python:
time, requests, random, bs4, os, json, notify2, gi.repository.GdkPixbuf, sys, subprocess, datetime.

Before strating:

1) change "os.chdir("/home/vodka/scripts/python/steam_gifts/")" 181 line to you path.

2) edit "search.txt" at your wish

3) edit cookie.txt. For show cookies you may use https://addons.mozilla.org/ru/firefox/addon/view-cookies/ for firefox or find instruction on google for you browser.

4) Edit you browser headers. 186 line. You may show you header by http://www.procato.com/my+headers/ . You must edit every time when you browser was updated.

Program idea:
1) Firstly bot enter giveaways grom you wishlist

2) After bot search giveaways from searc.txt

3) In end, bot enter to all giveaways, random

4) Bot sleep near 1 hour

На русском:
Работает только на ОС Linux! При желании можно перенести на Windows, убрав пару модулей и изменив пути. Но мне это не интересно. В случае бана аккаунта на steamgifts автор программы не несёт ответсвенности. Но я использую свою программу уже месяц, проблем нет. 

Бот для всеми известного сайта http://www.steamgifts.com/ Для запуска нужен Python 3 и вышеперечисленные модули.

Перед тем, как запустить программу:

1) Измените директорию в 181 строке на вашу

2) Отредактируйте search.txt по вашему желанию

3) Отредактируйте файл cookie.txt. Для просмотра ваших кук можно воспользоваться расширением https://addons.mozilla.org/ru/firefox/addon/view-cookies/ , либо найдите инструкцию в гугле для вашего браузера

4) Обязательно отредактируйте ваш заголовок браузера. 186 строка. Посмотреть заголовок можно на сайте http://www.procato.com/my+headers/ вы должны редактировать файл каждый раз после обновления вашего браузера или переустановки ОС.

Работа программы:

Вступление в раздачи происходит по трём критериям. Перечислены в порядке возрастания приоритета:

1) Вступление в раздачи из вашего списка желания

2) Поиск раздач с играми из файла search.txt

3) Вступление в случайные раздачи.

4) Бот уходит на сон, приблизительно на час. Далее всё по новой.
