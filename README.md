> [!CAUTION]
> БЕТА, РЕЛИЗА ЕЩЕ НЕ БЫЛО
<!-- https://github.com/orgs/community/discussions/16925 -->

# Кинопоиск3 - плагин для Plex Media Server (PMS)
<!-- https://shields.io/badges/git-hub-release -->
![CI][release-image]
[![][version-image]][changelog-url]
[![Release date][release-date-image]][release-url]
[![][version-beta-image]][changelog-url]
[![][license-image]][license-url]
[![GitHub issues][issues-opened]][issue-url]

# Почему и зачем.
В первую очередь хочу выразить искреннюю благодарность и восхищение Artem Mirotin aka [@amirotin](https://github.com/amirotin), Aleksey Ganuta aka [@Jenstel](https://github.com/Jenstel) и Vladimir Sharapov aka @EvelRus, которые являются авторами плагина для Plex Media Server (PMS) [Kinopoisk.bundle](https://github.com/Jenstel/Kinopoisk.bundle).</br>
Увы, последнее обновление которого - март 2021, и изменения в API kinopoiskapiunofficial.tech сделали этот плагин малопригодным для использования.</br>
## Назначение .
Плагин для [Plex Media Server (PMS)](https://www.plex.tv/) - медиасервера для NAS - позволяющий получить метаданные для файлов фильмов и сериалов через  [неофициальное API](https://kinopoiskapiunofficial.tech/) к информации по фильмам и сериалам сайта [Кинопоиск](https://www.kinopoisk.ru/).
Данная реализация архитектурно более проста, чем [Kinopoisk.bundle](https://github.com/Jenstel/Kinopoisk.bundle), здесь Кинопоиск единственный источник данных.</br>
Удалось добавить некоторые фишки, отсутствующие в оригинальном [Kinopoisk.bundle](https://github.com/Jenstel/Kinopoisk.bundle). При этом, хотя очень многое в коде и алгоритмах взято из оригинального плагина, архитектура полностью переработана, плагин значительно проще великолепного оригинала.</br>
И, несмотря на морфологическую конвергенцию, между собой данный плагин и Kinopoisk.bundle не совместимы принципиально.


# Использование
> [!IMPORTANT]  
> У меня торрент клиент скачивает фильмы и сериалы в папки Films и Serials.</br>
> Эти же папки в настройках PMS являются библиотеками для соответственно фильмов и сериалов.</br> 
> После успешной закачки автоматически стартует данный агент (см. [Настройки](#настройки))</br>
> В случае, если автосопоставление не сработало, что изредка бывает, сопоставляю вручную.


## Преимущества
Русский Кинопоиск и работающий плагин.

### Сопоставление
#### Поиск - автоматический и ручной
- При автозапуске ищет одновременно и по оригинальному имени файла, и по его транслителированному значению. (например, "Missiya_Serenity_(2005).BDRip-AVC.aac_[All.Films][RG].mkv" в результате объеденит 2 поиска - по "Missiya Serenity" и по "Миссия Серенити", заменив на пробел "_" и "."в имени)
- В списке результатов наименования могут<sup>[1](#myfootnote1)</sup> отображать кроме русского, еще и:
  - тип: F:фильм, M:многосерийный, V:видео, S:сериал, T:tv-шоу
  - оригинальное название, или английское
  - страну производства
  - жанр(ы)
> [!TIP]
> <a name="myfootnote1">1</a>: Задаётся в [Настройках](#настройки) 

#### Скоринг - оценка совпадения результатов поиска:
- по наименованию, рассчитывая [расстояние Левенштейна](https://ru.wikipedia.org/wiki/Расстояние_Левенштейна) (80%)
- по типу - учитывает фильм/сериал (5%)
- по году, отсутствие года - не так важно в весе, как разница с годом поиска. (15%)

#### Апдейт метаданных:
- обновление метаданных: основных, закачка постеров и обоев многопоточная и использует стороннюю библиотеку request - вместо 10сек на json - 0,3-0,5сек., на картинку вместо 6-8 сек - 2-4сек
- загружаются данные по прокату/выпуску
- штат - актеры, сценаристы, режиссеры
- обзоры с кинопоиска

> [!WARNING]  
> В некоторых фильмах и сериалах в API имеется и отдается лишь часть информации, например, нет наименований отдельных серий и синопсиса сериалов, или нет года выхода. Или нет оценок Кинопоиска или файлов с постерами и фонами. Естественно, в этом случае их не будет и в предоставлении информации плагина в PMS.




### Фильмы



### Сериалы
Кроме того, что реализовано для метаданных в фильмах, для сериалов плагин еще и:

<details>
<summary>Умеет работать с несколькими сезонами</summary>
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_2_seasones.png" alt="Несколько сезонов сериала">
</details>

<details>
<summary>Отображает наименования отдельных серий</summary>
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_ser_names.png" alt="В списке серий сезона - наименования серий">
</details>

<details>
<summary>Подробная информация и синопсис каждой серии</summary>
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_one_serie.png" alt="Подробная информация о каждой серии">
</details>

<details>
<summary>Загружает список актеров</summary>
Что мне НЕ нравится - в кружках фото от кинопоиска режет головы.
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_actors.png" alt="Актерский состав">
</details>

<details>
<summary>Многопоточно грузит постеры и фоны</summary>
По умолчанию назначается первый попавшийся, но в настройках можно выбрать и другой.
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_posters.png" alt="Постеры и фоны">
</details>


## Недостатки и особенности

R&D:
:: make_request = if not data
:: детализация по stuff? отдельная инфа по актеру - возможно?
:: ?? отдельный агент для Актеров? новый агент - Актеры, загрузка фото, биографии
:: надо ли clear() для старых proxie?
:: запуск картинок и актеров в отдельном треде? еще один плагин? передача ключа?
:: При запуске Сериалы - ... - Управление библиотекой - Обновить все метаданные: запускается сразу update - без search
:: в кружках фото актеров от кинопоиска режет головы.



```diff
Сравнение с Kinopoisk.bundle:
! Загрузка рейтингов для фильмов
+  * Kinopoisk
-  * Rotten Tomatoes
+  * IMDb
-  * The Movies Database
+ Источники рецензий на фильмы
+  - Kinopoisk
-  - Rotten Tomatoes
- Загрузка трейлеров фильмов
- Загрузка дополнительных материалов (сцены, интервью)
! Загрузка английских имен актеров
- Приоритет локализованных обложек фильмов
- Поддержка прокси-серверов (http, sock5)
```





# Установка
## Plex Media Server
Исходим из того, что [Plex Media Server](https://www.plex.tv/media-server-downloads/) для вашей операционной системы уже установлен.
Иначе зачем мог бы понадобиться плагин к нему?

## Latest версия
Скачать актуальную стабильную версию [Kinopoisk3.bundle](https://github.com/lugovskovp/Kinopoisk3.bundle/releases/latest) (Раздел Assets).
Плагин в активной доработке, практически почти каждый коммит автоматически генерит новую версию, поэтому в настройках (см.[Настройки](https://github.com/lugovskovp/Kinopoisk3.bundle/tree/beta#настройки)) рекомендую включить автообновление на стабильную версию.

## Распаковка в папку плагинов
Расположение папки плагинов Plex (папки Plug-ins) в разных операционных системах:
```
* '%LOCALAPPDATA%\Plex Media Server\'                                        # Windows Vista/7/8
* '%USERPROFILE%\Local Settings\Application Data\Plex Media Server\'         # Windows XP, 2003, Home Server
* '$HOME/Library/Application Support/Plex Media Server/'                     # Mac OS
* '$PLEX_HOME/Library/Application Support/Plex Media Server/',               # Linux
* '/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/', # Debian,Fedora,CentOS,Ubuntu
* '/usr/local/plexdata/Plex Media Server/',                                  # FreeBSD
* '/usr/pbi/plexmediaserver-amd64/plexdata/Plex Media Server/',              # FreeNAS
* '${JAIL_ROOT}/var/db/plexdata/Plex Media Server/',                         # FreeNAS
* '/c/.plex/Library/Application Support/Plex Media Server/',                 # ReadyNAS
* '/share/MD0_DATA/.qpkg/PlexMediaServer/Library/Plex Media Server/',        # QNAP
* '/volume1/Plex/Library/Application Support/Plex Media Server/',            # Synology, Asustor
* '/raid0/data/module/Plex/sys/Plex Media Server/',                          # Thecus
* '/raid0/data/PLEX_CONFIG/Plex Media Server/'                               # Thecus Plex community
* '/Volume1/Plex/Library/Application Support/Plex Media Server'              # TOS 5.0 | TOS 6.0
```

## Права в unix ОС
На примере Debian / Ubuntu проверка наличия необходимых библиотек и/или установки всего необходимого
```
sudo apt update && sudo apt install -y git
cd /var/lib/plexmediaserver/Library/Application\ Support/Plex\ Media\ Server/Plug-ins/
sudo git clone https://github.com/Jenstel/Kinopoisk.bundle.git
sudo chown -R plex:plex Kinopoisk.bundle/
sudo systemctl restart plexmediaserver
```

## Ключ kinopoiskapiunofficial.tech
Для функционирования плагину требуется токен API сервиса [kinopoiskapiunofficial](https://kinopoiskapiunofficial.tech/).
Для получения токена необходимо зарегистрироваться на [Kinopoisk API Unofficial
](https://kinopoiskapiunofficial.tech/rates) и выбрать тарифный план.
Базовый доступ бесплатен: до 500 запросов в сутки.
Расширенный доступ за 500 руб. / месяц уже позволяет выполнять до 10 000 запросов в сутки.
На получение информации по одному фильму потребуется порядка 10-15 запросов. 

https://kinopoiskapiunofficial.tech/documentation/api/#/films/get_api_v2_1_films_search_by_keyword


## Настройки




# Разработчикам
Для самостоятельного внесения изменений необходимо выполнить 
```git clone git@github.com:lugovskovp/Kinopoisk3.bundle.git```. <br/>
Скачивание ZIP архива стабильной версии **не подходит** - в архиве будет только сам плагин, без GH workflows, файлов настроек и папки документации.
Отладка и профайлинг отключаются настройкой.

## Пожелания к доработке
Если есть пожелания к доработке какой-то функции, или необходимо сообщить о проблеме - достаточно завести [обсуждение](https://github.com/lugovskovp/Kinopoisk3.bundle/issues/new/choose) на странице проекта.


## Changelog
Файл изменений версий [CHANGELOG][changelog-url] формируется автоматически CI, настроенным в GitHub Actions, поэтому, боюсь, он может показаться достаточно неудобным для пользователя.


## License
This project is released under the [GPLv3 License][license-url].


## Контрибуторам
Как-то не ожидаются такие.


<!-- Links: -->
[release-url]: https://github.com/lugovskovp/Kinopoisk3.bundle
[changelog-url]: https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/CHANGELOG.md

[release-image]: https://github.com/lugovskovp/Kinopoisk3.bundle/actions/workflows/release.yml/badge.svg?branch=master
[release-url]: https://github.com/lugovskovp/Kinopoisk3.bundle/actions/workflows/release.yml

[version-image]: https://img.shields.io/github/v/release/lugovskovp/Kinopoisk3.bundle
[version-beta-image]: https://img.shields.io/github/v/release/lugovskovp/Kinopoisk3.bundle?include_prereleases
[release-date-image]: https://img.shields.io/github/release-date/lugovskovp/Kinopoisk3.bundle

[license-url]: https://github.com/lugovskovp/Kinopoisk3.bundle/blob/main/LICENSE
[license-image]: https://img.shields.io/github/license/lugovskovp/Kinopoisk3.bundle

[issues-opened]: https://img.shields.io/github/issues/lugovskovp/Kinopoisk3.bundle
[issue-url]: https://github.com/lugovskovp/Kinopoisk3.bundle/issues



-----------
Текщие значения настроек:
"c:\Users\plugo\AppData\Local\Plex Media Server\Plug-in Support\Preferences\com.plexapp.plugins.kinopoisk3.xml" 

