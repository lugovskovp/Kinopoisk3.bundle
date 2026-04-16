# -*- coding: utf-8 -*-
# coding=utf-8

# find in \Contents\Library\Shared
import requests             # [а к нему еще chardet, urllib3, certifi, idna]      # type: ignore 
import re

from config import API_BASE_URL
from debug import d, w            #, log_timing

# -------------------------------------------------------------

def AppendSearchResult(results, id, name=None, year=-1, score=0, lang=None):
  # Добавить к результату(там) поиска еще один результат
  new_result = dict(id=str(id), name=name, year=int(year), score=score, lang=lang)
  if isinstance(results, list):
      results.append(new_result)
  else:
      results.Append(MetadataSearchResult(**new_result)) # type: ignore
  return

# -------------------------------------------    
def get_json(url):
  ''' Получить json 
  
  url - URL с endpoint и параметрами 
  '''
  ApiKey = Prefs['api_key']   # type: ignore
  headers = {
      'Accept': 'application/json',
      'X-API-KEY': ApiKey,              
      'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'
      }
  try:
    response = requests.get(url, headers=headers)  # data = r.content  # Content of response
  except requests.ConnectionError as e:
    # TODO ERR_CONNECTION_TIMED_OUT - get away?
    Core.log.error("OOPS!! Connection Error. Или Вы не в интернете, или http://kinopoiskapiunofficial.tech вне доступа.\n") # type: ignore
    Core.log.error(str(e))  # type: ignore   
    return False
  except:
    Core.log.error("Какая-то ошибка, но не Connection Error.")  # type: ignore
    return False
  if response.status_code == 200:
    # best way - go away
    return  response.json()
  # -------------- что-то пошло не так
  if response.status_code == 404:
    Core.log.error("HTTP error 404, не найден %s" % (url))  # type: ignore
    return False
  if response.status_code == 401:
    Core.log.error("HTTP error 401, не позволено: не найден валидный токен")  # type: ignore
    return False
  if response.status_code == 402:
    Core.log.error("HTTP error 402, дневная квота исчерпана")  # type: ignore
    return False
  #status_code == 401:    You don't have permissions There are not valid token  
  #status_code == 402:    You exceeded the quota.
  #status_code == 429:    Rate limit exceeded
  Core.log.error("Не, ну точно ошибка %s в %s" % (response.status_code, url))  # type: ignore
  Core.log.error("Описание ошибки %s: %s" % (response.status_code, response.content))  # type: ignore
  return False


def APItokenRemains():
  '''
  Return False if token err happened
  Return int - Qty remains dailyQuota for use.
  #/api/v1/api_keys/{apiKey}  #получить данные об api key 
  '''
  url = '%s/api/v1/api_keys/%s' % (API_BASE_URL, Prefs['api_key'] )  # type: ignore
  json = get_json(url)
  if not json or json == 'False':
    return False
  # if not json:
  #   # returned false
  #   return False
  BIG_VALUE = 1000
  d(json)
  dq = json.get("dailyQuota", '')
  if not dq:
    w(u"APItokenRemains:: wrwre are not daylyQuoya in json")      
    return False
  value = dq.get("value")
  used  = dq.get("used")
  w(u"APItokenRemains::dailyQuota value:%s used:%s" % (value, used)) 
  accountType = json.get("accountType") or 'unknown account type'
  if accountType == 'UNLIMITED':
    remains = BIG_VALUE
  else:
    if used >= value:
      w(u"APItokenRemains::exceeded dailyQuota value:%s used:%s" % (value, used))                   # type: ignore
      return False    #You exceeded the quota. You have sent 517 request, but available 500 per day
    else:
      remains = value - used
  Log(u"APItokenRemains:: accountType:%s remains:%s" % (accountType, remains))                  # type: ignore
  return remains


def translit2ru(text):
  '''Замена транслита русскими буквами'''
  multiple_letters = {u'sch': u'щ', u'sh': u'ш', u'zh': u'ж', u'ts': u'ц', u'ch': u'ч',
                      u'yu': u'ю', u'iu': u'ю', u'ya': u'я', u'ia': u'я', u'yo': u'ё'} # +[[ 'Liubopytnaya', 'лиубопытная']]
  single_letters = {u'a': u'а',  u'b': u'б',  u'v': u'в',  u'g': u'г',  u'd': u'д', 
                      u'e': u'е',  u'z': u'з',  u'i': u'и',  u'j': u'й',  u'k': u'к', 
                      u'l': u'л',  u'm': u'м',  u'n': u'н',  u'o': u'о',  u'p': u'п', 
                      u'r': u'р',  u's': u'с',  u't': u'т',  u'u': u'у',  u'f': u'ф', 
                      u'h': u'х',  u'y': u'ы',  u'w': u'в'}
  text = text.lower()                     #for simple dicts
  for en_let, ru_let in multiple_letters.items():
      text = text.replace(en_let, ru_let) # replace 'complex' letters
  for en_let, ru_let in single_letters.items():
      text = text.replace(en_let, ru_let) # replace simple letters
  return text.encode("utf-8")  


def getGUIDs(guid):
  ''' возвращает dict с kpId и imdbId'''
  guids = { 'kpId' : '',
           'imdbId' : ''}
  kpSearch = re.search('(kp(\d*))', guid)
  if kpSearch and kpSearch.group(2):
    guids['kpId'] = kpSearch.group(2)
  imdbSearch = re.search('(tt(\d*))', guid)
  if imdbSearch and imdbSearch.group(1):
    guids['imdbId'] = imdbSearch.group(1)  
  return guids


def resurrectMetadataId(id):
  ''' при выборе Prefs["showSerialSeasons"]: восстановить (id, seasonNum)'''
  sea = ''
  res = (id, sea)
  r = re.search('S(\d*):(\d*)', id)
  if r and r.group(2):
    res = (r.group(2), int(r.group(1)))
  return res
