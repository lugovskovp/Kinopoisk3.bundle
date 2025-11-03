# -*- coding: utf-8 -*-
# coding=utf-8

# find in \Contents\Library\Shared
import requests             # [а к нему еще chardet, urllib3, certifi, idna]      # type: ignore 
import traceback            # для get_json()
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


def translit2ru(text):
  '''Замена транслита русскими буквами'''
  multiple_letters = {u'sch': u'щ', u'sh': u'ш', u'zh': u'ж', u'ts': u'ц',
                      u'ch': u'ч', u'yu': u'ю', u'ya': u'я', u'yo': u'ё'}
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


def get_json(url):
  headers={
      'Accept': 'application/json',
      'X-API-KEY': Prefs['api_key'], # type: ignore
      'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'
      }
  try:
    rj = requests.get(url, headers=headers).json()   # data = r.content  # Content of response
  except:
    Log("\n\n err::Except in get_json - requests.get(url=%s)" % url)      # type: ignore
    Log(traceback.format_exc())                                           # type: ignore
    return                 # в случае ошибки, вернуть пустую строку
  if 'message' in rj:    # признак ошибки
    Log("\n\n err::Попытка поиска без ключа: %s" % rj['message'])         # type: ignore
    return rj
  return rj



