# -*- coding: utf-8 -*-
# coding=utf-8
# import re

# find in \Contents\Library\Shared
import requests             # type: ignore # [а к нему еще chardet, urllib3, certifi, idna]

# константы
NAME = 'Кинопоиск3' # % VER
VER = '0.0.1'
version_path = Core.storage.join_path(Core.bundle_path, 'Contents', 'VERSION') # type: ignore
if Core.storage.file_exists(version_path): # type: ignore
  str_version = Core.storage.load(version_path) # type: ignore
  VER = str_version.split()[0]
LANGUAGES = [Locale.Language.Russian, Locale.Language.English, Locale.Language.NoLanguage]  # type: ignore # [Locale.Language.Russian, Locale.Language.English, Locale.Language.NoLanguage,]

# Update vars
UPDATER_REPO = 'lugovskovp'
UPDATER_STABLE_URL = 'https://api.github.com/repos/%s/Kinopoisk3.bundle/releases/latest'
  #https://api.github.com/repos/lugovskovp/Kinopoisk3.bundle/releases/latest
UPDATER_BETA_URL = 'https://api.github.com/repos/%s/Kinopoisk3.bundle/tags?per_page=1'
  #https://api.github.com/repos/lugovskovp/Kinopoisk3.bundle/tags?per_page=1
UPDATER_ARCHIVE_URL = 'https://github.com/%s/Kinopoisk3.bundle/archive/refs/tags/'
  #https://github.com/lugovskovp/Kinopoisk3.bundle/archive/refs/tags/v1.6.0.zip
  #https://github.com/lugovskovp/Kinopoisk3.bundle/archive/refs/tags/v1.6.1-beta.5.zip
MIN_UPDATE_INTERVAL = 10

# URLS      FILM_xxxx - для функций получения инфо с кинопоиска для update
API_BASE_URL      = 'https://kinopoiskapiunofficial.tech'
KEYWORD_SEARCH    = '/api/v2.1/films/search-by-keyword?keyword=%s&page=%s'
FILM_DETAILS      = '/api/v2.2/films/%s'
FILM_POSTERS      = '/api/v2.2/films/%s/images?type=%s&page=1'
FILM_DISTRIBUTION = '/api/v2.2/films/%s/distributions'
FILM_STAFF        = '/api/v1/staff?filmId=%s'
FILM_REVIEW       = '/api/v2.2/films/%s/reviews?page=1&order=DATE_DESC'
SERIAL_SEASONS    = '/api/v2.2/films/%s/seasons'

UNKNOWN_YEAR = 1900
SCORE_WEIGHT_NAME = 80
SCORE_WEIGHT_YEAR = 15  # 100 - SCORE_WEIGHT_NAME
SCORE_WEIGH_JANRE = 5

PREFIX = '/video/kino'
TITLE = 'Агент Кинопоиск Unofficial'
ART = 'art-default.png'
ICON = 'icon-default.png'


import traceback

def get_json(url):
  headers={
      'Accept': 'application/json',
      'X-API-KEY': Prefs['api_key'], # type: ignore
      'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'
      }
  try:
    rj = requests.get(url, headers=headers).json()   # data = r.content  # Content of response
  except:
    Log("\n\n err::Except in get_json - requests.get(url=%s)" % url) # type: ignore
    Log(traceback.format_exc())       # type: ignore
    return                 # в случае ошибки, вернуть пустую строку
  if 'message' in rj:    # признак ошибки
    Log("\n\n err::Попытка поиска без ключа: %s" % rj['message']) # type: ignore
    return rj
  return rj

      
def lev_ratio(s1, s2):
  '''levR  = abs( Util.LevenshteinDistance(search_title.lower(), foundTitle.lower()) )'''
  distance = Util.LevenshteinDistance(s1, s2) # type: ignore
  max_len = float(max([ len(s1), len(s2) ]))
  s1 = s1.lower()
  s2 = s2.lower()
  ratio = 0.0
  try:
    ratio = float(1 - (distance/max_len))
  except:
    pass
  return ratio


def lev_score(nameRu, nameEn, title):
  # scoring по имени
  lev = max(lev_ratio(title, nameRu), lev_ratio(title, nameEn))     # levR if levR > levE else levE
  score = int(SCORE_WEIGHT_NAME * lev)  # тут score max = SCORE_WEIGHT_NAME
  return score


def d(*args):
  '''Включить подробную отладку'''
  if Prefs['trace']: # type: ignore
    args = list(args)
    args[0] = '     #### %s' % args[0]
    Log('\n'.join(map(str, args)))  # type: ignore


# --------------------------- debug functions ---------------------------

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

      
def log_timing(func):
  ''' Замер времени выполнения функции, декоратор, миллисекунды'''
  def wrapper(*args, **kwargs):
      # "Действие перед выполнением функции"
      msStart = getMilliseconds(Datetime.Now()) # type: ignore
      func_name = ("%s" % func).split(" ")[1] #- тут имя функции 
      strArgs = ', '.join(map(str, list(args)))
      d("<<<<<<< start::%s (%s)" % (func_name, strArgs))
      func(*args, **kwargs)
      # ("Действие после выполнения функции")
      d(">>>>>>> end::%s, duration=%s\n"  % (func_name, (getMilliseconds(Datetime.Now()) - msStart))) # type: ignore
  return wrapper


def getMilliseconds(dt):
  ''' Только миллисекунды, в полночь - тыква'''
  # dt waiting as '2025-01-25 12:41:53.921000'
  strDt = "%s" % dt                 # to str
  arrDt = strDt.split(" ")          # ["2025-01-25", "12:41:53.921000"]
  if len(arrDt) != 2:               # err
    return
  strTime = arrDt[1]                # 12:41:53.921000
  arrTime = strTime.split(":")      # ["12", "41", "53.921000"]
  arrTime.reverse()                 # ["53.921000", "41", "12"]
  sec = arrTime[0].split(".")       #  ["53", "921000"]
  arrTime[0] = sec[0]               # ["53", "41", "12"]
  if len(arrTime) != 3:             # err   проверку на 3 - и выйти, если не так.
    return
  seconds = 0
  for i in range(0, 3):
    seconds += int(arrTime[i]) * (60**i)
  seconds = seconds * 1000          # milliseconds
  seconds += int(sec[1])/1000       # 921000 -> 921 
  return int(seconds)               #     milliseconds   


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

