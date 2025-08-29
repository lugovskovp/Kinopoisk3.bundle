# -*- coding: utf-8 -*-
# coding=utf-8

# find in \Contents\Library\Shared
import requests             # [а к нему еще chardet, urllib3, certifi, idna]      # type: ignore 
import traceback            # для get_json()



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



