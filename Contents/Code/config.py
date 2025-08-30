# -*- coding: utf-8 -*-
# coding=utf-8

# константы ===============================================================================

NAME = u'Кинопоиск3' 
VER = '0.0.1'
PREFIX = '/video/kino'
TITLE = u'Агент Кинопоиск Unofficial'
ART = 'art-default.png'
ICON = 'icon-default.png'
LANGUAGES = [Locale.Language.Russian, Locale.Language.English, Locale.Language.NoLanguage]  # type: ignore # [Locale.Language.Russian, Locale.Language.English, Locale.Language.NoLanguage,]
# значение версии взять из файла VERSION
version_path = Core.storage.join_path(Core.bundle_path, 'Contents', 'VERSION') # type: ignore
if Core.storage.file_exists(version_path):                                     # type: ignore
  str_version = Core.storage.load(version_path)                                # type: ignore
  VER = str_version.split()[0]

REQUEST_QTY_SEARCH_MIN = 20   # при старте поиска должно оставаться не менее Х запросов

# Update vars
UPDATER_REPO = 'lugovskovp'
UPDATER_STABLE_URL = 'https://api.github.com/repos/%s/Kinopoisk3.bundle/releases/latest'
UPDATER_BETA_URL = 'https://api.github.com/repos/%s/Kinopoisk3.bundle/tags?per_page=1'
UPDATER_ARCHIVE_URL = 'https://github.com/%s/Kinopoisk3.bundle/archive/refs/tags/'
UPDATE_INTERVAL_MIN = 10    # MINIMAL INTERVAL = 10min

# URLS      FILM_xxxx - для функций получения инфо с кинопоиска для update и поиска
API_BASE_URL      = 'https://kinopoiskapiunofficial.tech'
KEYWORD_SEARCH    = '/api/v2.1/films/search-by-keyword?keyword=%s&page=%s'
FILM_DETAILS      = '/api/v2.2/films/%s'
FILM_POSTERS      = '/api/v2.2/films/%s/images?type=%s&page=1'
FILM_DISTRIBUTION = '/api/v2.2/films/%s/distributions'
FILM_STAFF        = '/api/v1/staff?filmId=%s'
FILM_REVIEW       = '/api/v2.2/films/%s/reviews?page=1&order=DATE_DESC'
SERIAL_SEASONS    = '/api/v2.2/films/%s/seasons'

# scoring
MAX_DELTA_YEAR = 25 / 1 # вся бОльшая дельта - бессчысленна для скоринга
UNKNOWN_YEAR = 1900     # значение неизвестного года
MAX_VALID_YEAR  = 2035  # максимально допустимый год производства
SCORE_WEIGHT_NAME = 80  # % веса имени - при полном совпадении с найденным - 80
SCORE_WEIGHT_YEAR = 15  # % веса года
SCORE_WEIGH_JANRE = 5   # % веса типа фильма (для фильмов и сериалов в [ 'FILM', 'VIDEO', 'TV_SERIES', 'MINI_SERIES', 'TV_SHOW' ])



# ===============================================================================
