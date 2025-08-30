# -*- coding: utf-8 -*-
# coding=utf-8

import requests             # [а к нему еще chardet, urllib3, certifi, idna]      # type: ignore 

# константы ===============================================================================

NAME = u'Кинопоиск3' # % VER
VER = '0.0.1'
PREFIX = '/video/kino'
TITLE = 'Агент Кинопоиск Unofficial'
ART = 'art-default.png'
ICON = 'icon-default.png'

version_path = Core.storage.join_path(Core.bundle_path, 'Contents', 'VERSION') # type: ignore
if Core.storage.file_exists(version_path):                                    # type: ignore
  str_version = Core.storage.load(version_path)                               # type: ignore
  VER = str_version.split()[0]
LANGUAGES = [Locale.Language.Russian, Locale.Language.English, Locale.Language.NoLanguage]  # type: ignore # [Locale.Language.Russian, Locale.Language.English, Locale.Language.NoLanguage,]

REQUEST_QTY_SEARCH_MIN = 20   # при поиске должно оставаться не менее

# Update vars
UPDATER_REPO = 'lugovskovp'
UPDATER_STABLE_URL = 'https://api.github.com/repos/%s/Kinopoisk3.bundle/releases/latest'
UPDATER_BETA_URL = 'https://api.github.com/repos/%s/Kinopoisk3.bundle/tags?per_page=1'
UPDATER_ARCHIVE_URL = 'https://github.com/%s/Kinopoisk3.bundle/archive/refs/tags/'
UPDATE_INTERVAL_MIN = 10    # MINIMAL INTERVAL = 10min

# URLS      FILM_xxxx - для функций получения инфо с кинопоиска для update
API_BASE_URL      = 'https://kinopoiskapiunofficial.tech'
KEYWORD_SEARCH    = '/api/v2.1/films/search-by-keyword?keyword=%s&page=%s'
FILM_DETAILS      = '/api/v2.2/films/%s'
FILM_POSTERS      = '/api/v2.2/films/%s/images?type=%s&page=1'
FILM_DISTRIBUTION = '/api/v2.2/films/%s/distributions'
FILM_STAFF        = '/api/v1/staff?filmId=%s'
FILM_REVIEW       = '/api/v2.2/films/%s/reviews?page=1&order=DATE_DESC'
SERIAL_SEASONS    = '/api/v2.2/films/%s/seasons'

# scoring
UNKNOWN_YEAR = 1900
MAX_VALID_YEAR  = 2035
SCORE_WEIGHT_NAME = 80
SCORE_WEIGHT_YEAR = 15  # 100 - SCORE_WEIGHT_NAME
SCORE_WEIGH_JANRE = 5



# ===============================================================================
