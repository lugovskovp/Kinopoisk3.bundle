# -*- coding: utf-8 -*-
# coding=utf-8

import requests             # [а к нему еще chardet, urllib3, certifi, idna]      # type: ignore 

# from common_upd import load_distribution, load_episodes, load_gallery, load_metadata, load_reviews, load_staff # общие для апдейта в классах

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

def APItokenRemains():
  '''
  Return False if token err happened
  Return int - Qty remains dailyQuota for use.
  #/api/v1/api_keys/{apiKey}  #получить данные об api key 
  '''
  valid = False
  key = Prefs['api_key']                                                                # type: ignore
  url = '%s/api/v1/api_keys/%s' % (API_BASE_URL, key)
  headers={
    'Accept': 'application/json',
    'X-API-KEY': key, # type: ignore
    'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'
    }
  try:
    response = requests.get(url, headers=headers)  # data = r.content  # Content of response
  except:
    pass
  status_code = response.status_code
  d(u"APItokenRemains::response code:%s json:%s" % (status_code, response.json()))                  # type: ignore
  if status_code != 200:
    # что-то пошло не так
    #status_code == 401:    You don't have permissions There are not valid token  
    #status_code == 402:    You exceeded the quota.
    #status_code == 429:    Rate limit exceeded
    w("APItokenRemains::ERROR %s: %s" % (status_code, response.json()["message"]))                  # type: ignore
    return False
  else:
    # 200, ключ есть, ответ есть. Может, даже остались в квоте попытки.
    json = response.json()
    accountType = json["accountType"]
    dailyQuota = json["dailyQuota"]["value"]
    used = json["dailyQuota"]["used"]
    if accountType == 'UNLIMITED':
      remains = 1000
    else:
      if used >= dailyQuota:
        w(u"APItokenRemains::exceeded quota:%s used:%s" % (dailyQuota, used))                   # type: ignore
        return False    #You exceeded the quota. You have sent 517 request, but available 500 per day
      else:
        remains = dailyQuota - used
    Log(u"APItokenRemains:: accountType:%s remains:%s" % (accountType, remains))                  # type: ignore
  return remains
  
  
# --------------------------- log decoration functions ---------------------------

def pp_json(json, lev=0):
  '''Pretty print json'''
  res = ""
  if not isinstance(json, dict):    # это может быть и list
    return "--%s-- Это не dict JSON !!!" % json
  trail = ""
  for i in range(0, lev):
    trail += "  "
  for key in json:
    val = json[key]
    if isinstance(val, list):
      res += "%s%s:[\n" % (trail, key)
      lev += 1
      for i, el in enumerate(val):
        res += trail
        res += pp_json(val[i], lev)
      res += "%s]\n" % trail
    else:
      res += ("%s%s: %s\n" % (trail, key, json[key]))
  return res



def get_media_data(media, isUpdate=False):
  ''' отображает данные для search media - Movie|TV_Show'''
  m = "\nmedia:\n"
  m += ".media.primary_agent : %s\n" % media.primary_agent
  m += ".media.primary_metadata : %s\n" % media.primary_metadata
  m += ".media.guid : %s\n" % media.guid
  m += ".media.filename : %s\n" % media.filename
  m += ".media.parent_metadata : %s\n" % media.parent_metadata
  # 
  m += ".media.tree : %s\n" % media.tree
  m += ".media.id : %s\n" % media.id
  m += ".media.hash : %s\n" % media.hash
  m += ".media.originally_available_at : %s\n" % media.originally_available_at
  if hasattr(media, 'season'):       # if TV_Show
    m += ".media.parentGUID : %s\n" % media.parentGUID    # Movie has no the attribute
    #m += "TV_Show. : %s\n" % 
    pass
  else:                        # Movie
    m += "Movie.media.name : %s\n" % media.name
    m += "Movie.media.openSubtitlesHash : %s\n" % media.openSubtitlesHash
    m += "Movie.media.year : %s\n" % media.year
    m += "Movie.media.duration : %s\n" % media.duration
    #m += "movie. : %s\n" % 
  return m