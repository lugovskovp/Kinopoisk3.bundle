# БЕТА, РЕЛИЗА ЕЩЕ НЕ БЫЛО

# Кинопоиск3 - плагин для Plex
<!-- https://shields.io/badges/git-hub-release -->
![CI][release-image]
[![][version-image]][changelog-url]
[![Release date][release-date-image]][release-url]
[![][version-beta-image]][changelog-url]
[![][license-image]][license-url]
[![GitHub issues][issues-opened]][issue-url]

# Почему и зачем.
Искренняя благодарность Artem Mirotin aka [@amirotin](https://github.com/amirotin), Aleksey Ganuta aka [@Jenstel](https://github.com/Jenstel) и Vladimir Sharapov aka @EvelRus, которые являются авторами плагина для Plex Media Server (PMS) [Kinopoisk.bundle](https://github.com/Jenstel/Kinopoisk.bundle).</br>
Увы, последнее обновление которого - март 2021, и изменения в API kinopoiskapiunofficial.tech сделали этот плагин малопригодным для использования.</br>
Данная реализация архитектурно более проста, единственный источник данных - неофициальное API Кинопоиска.</br>
Удалось добавить некоторые фишки, отсутствующие в оригинальном Kinopoisk.bundle. При этом, хотя очень многое в коде и алгоритмах взято из оригинального, архитектура полностью переработана, плагин значительно проще великолепного оригинала.</br>
И, несмотря на морфологическую конвергенцию, между собой данный плагин и Kinopoisk.bundle не совместимы принципиально.


# Использование
Торрент клиент у меня скачивает фильмы и сериалы в папки соответсвенно Films и Serials.</br>
Эти же папки использованы в настройках PMS для фильмов и сериалов.</br> 
После закачки ВРУЧНУЮ запускаю данный агент (см. [Настройки](https://github.com/lugovskovp/Kinopoisk3.bundle/tree/beta#настройки))</br>
Похоже, PMS с какого-то времени убрал автозапуск неродных плагинов.

## Преимущества

Поиск при сопоставлении:
- В списке результатов наименования могут<sup>[1](#myfootnote1)</sup> отображать:
  - тип: F:фильм, M:многосерийный, V:видео, S:сериал, T:tv-шоу
  - оригинальное название, кроме русского
  - страну производства
  - жанр(ы)
- Поиск одновременно и по оригинальному имени файла, и по его транслителированному значению. (например, "Missiya_Serenity_(2005).BDRip-AVC.aac_[All.Films][RG].mkv" в результате объеденит поиски по "Missiya Serenity" и по "Миссия Серенити", заменив на пробел "_" и "."в имени)

Скоринг:
- скоринг по наименованию 
- скоринг учитывает по типу - фильм/сериал
- SCORING по году если 1900 - просто добавить 75% макс скоринга, отсутствие года - не так важно, как отличие.
Апдейт метаданных:
- обновление метаданных - основных, закачка постеров, обоев
- сторонняя библиотека request - вместо 10сек на json - 0,3-0,5сек
- запрос катринок - постеров и обоев - многопоточная, вместо 6-8 сек - 3-4сек
- данные по прокату/выпуску
- штат - актеры, сценаристы, режиссеры
- обзоры с кинопоиска
- сломалась load_gallery - починил, переписал на неклассовую функцию, загрузка в параллельных потоках
- ejson = enhased json, return '' if no key in json
- переработка - вынести функции из классов чтобы максимально использовать один код для обоих классов
- metadata.art.validate_keys(valid_names) - art и posters после всей загрузки
- убрать лишнее из настроек Prefs
- всё то же самое - для сериалов
- в сериалах - эпизоды
- копию библиотеки с NAS - мелкий mp4 копировать и называть, как большие реальные файлы, доработать по прогону
- [TV_SERIES].[FILM] в результатах поиска?

В некоторых фильмах и сериалах в API отдается лишь часть информации, например, нет наименований отдельных серий и синопсиса сериалов, или нет года выхода. или нет оценок Кинопоиска или файлов с постерами и фонами. Естественно, в этом случае их не будет и в предоставлении информации плагина в PMS.

### Сопоставление - Поиск

### Сериалы

<details>
<summary>Умеет работать с несколькими сезонами</summary>
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_2_seasones.png" alt="Несколько сезонов сериала">
</details>

<details>
<summary>Отображение наименований отдельных серий</summary>
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_ser_names.png" alt="В списке серий сезона - наименования серий">
</details>

<details>
<summary>Подробная информация и синопсис каждой серии</summary>
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_one_serie.png.png" alt="Подробная информация о каждой серии">
</details>

<details>
<summary>Список актеров</summary>
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_actors.png.png" alt="Актерский состав">
</details>

<details>
<summary>Постеры и фоны</summary>
По умолчанию назначается первый попавшийся, но можно изменить в настройках, выбрав тот, что нравится более.
<img src="https://github.com/lugovskovp/Kinopoisk3.bundle/blob/master/pix/ser_posters.png.png" alt="Постеры и фоны">
</details>


### Фильмы




## Недостатки

При запуске Сериалы - ... - Управление библиотекой - Обновить все метаданные: запускается сразу update - без search



## Что в планах

TODO:
- не только manual, но и автоматический фоновый поиск и обновление метаданных (как авто запускать?)
- год из имени файла, если 1900
- распознавание имени файла? 
- добавляется id imdb|tmdb в guid
    вы можете найти фильм на IMDB или TMDB и ввести идентификатор в поле «Название» при поиске (для IMDB используйте формат tt12345678, а для TMDB — tmdb-123456789)
- инструкция в .md - как ставить, как выглядит
- обновление новых версий плагина с сайта (c github?)
- about info - добавить картинку
- TheTVDB в сериалах
- "message": "You exceeded the quota. You have sent 503 request, but available 500 per day"

CIt:
:: как запустить отдельный треад? DEBUG (runtime:1117) - Created a thread named 'start'
:: make_request = if not data
:: детализация по stuff? отдельная инфа по актеру - возможно?
- ?? отдельный агент для тяжелых картинок?
- ?? отдельный агент для Актеров? новый агент - Актеры, загрузка фото, биографии
- надо ли clear() для старых proxie?
- запуск картинок и актеров в отдельном треде? еще один плагин? передача ключа?





# Установка
Исходим из того, что [Plex Media Server](https://www.plex.tv/media-server-downloads/) для вашей операционной системы уже установлен.
Иначе зачем мог понадобиться плагин к нему.

## Latest версия
Скачать актуальную версию [Kinopoisk3.bundle](https://github.com/lugovskovp/Kinopoisk3.bundle/releases/latest) (Раздел Assets).
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

## Ключ kinopoiskapiunofficial.tech

https://kinopoiskapiunofficial.tech/

https://kinopoiskapiunofficial.tech/documentation/api/#/films/get_api_v2_1_films_search_by_keyword

## Настройки


# Разработка

## Пожелания к доработке
Если есть пожелания к доработке какой-то функции, или необходимо сообщить о проблеме - достаточно завести тикет на странице проекта:
[обсуждение](https://github.com/lugovskovp/Kinopoisk3.bundle/issues/new/choose)


## Changelog
Файл изменений версий [CHANGELOG][changelog-url] формируется автоматически, CI, настроенным в GitHub Actions, поэтому, боюсь он достаточно неудобен для простого пользователя.

## License
This project is released under the [GPLv3 License][license-url].

## Контрибуторам

Для самостоятельного внесения изменений необходимо выполнить ```git clone git@github.com:lugovskovp/Kinopoisk3.bundle.git```. Скачивание ZIP архива стабильной версии не годится - в архиве будет только сам плагин, без GH workflows, файлов настроек и папки документации.

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

<a name="myfootnote1">1</a>: Footnote content goes here

-----------
Текщие значения настроек:
"c:\Users\plugo\AppData\Local\Plex Media Server\Plug-in Support\Preferences\com.plexapp.plugins.kinopoisk3.xml" 

