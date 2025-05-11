# -*- coding: utf-8 -*-
# coding=utf-8
import re

# constants   
UNKNOWN_YEAR  = 1900       # грязно, эта же константа с этим же значением - в config.py
MAX_VALID_YEAR  = 2035

# -------------------------------------------------------------
class srch_params():
  '''Просто поскладём все параметры поиска в сюда'''
  isAgentMovies = True    #   1. Agent.Movies или Agent.TV_Shows
  isNewMatch    = True    #   2. Определить режим - сопоставление или исправление
  isManual      = False
  titles        = []      # массив str из 1 или 2 элементов, 0-имя, 1-транскрибированное имя
  year          = 0       # год выпуска - из формы поиска
  
  def __init__(self, media, manual):
    self.isAgentMovies = False if hasattr(media, 'season') else True
    self.isNewMatch = media.filename is None
    # media.filename == None когда сопоставления еще не было, первый раз нажато "Сопоставить"
    # media.filename == filename, когда (Fix Incorrect Match), сразу будет сразу попытка поиска по media.name
    self.isManual = manual
    self.titles = []
    self.titles.append(media.name if self.isAgentMovies else media.show)    # self.titles[0]
    search_year = 0
    #if not manual:
    if manual:    #TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   not manual after debug
      # т.е. значение - не из строки поиска, а из media.year, media.id, media.name
      self.titles[0] = re.sub(r'_', ' ', self.titles[0])     # в наименовании _ заменяем на пробелы
      self.titles[0] = re.sub(r'\.', ' ', self.titles[0])    # in result . to ' '
      # поиск автоматический. имя выглядит как "головоломка 2 2024" или "Missiya Serenity 2005 Dlrip"
      r = re.search("^(.+)((19|20)\d\d)(.*)$", self.titles[0])  # - регексп года, , что справа отбрасывается, .
      if r:
        self.titles[0] = r.group(1).strip()   # год извлекается
        search_year = int(r.group(2))           # что слева года - имя
        Log("Regexp search_year = %s, search_title = '%s'" % (search_year, self.titles[0])) # type: ignore
      # если имя уже русскими буквами - не добавляем ничего
      search_ru = translit2ru(self.titles[0])  # наименование часто транслитерируется англ. буквами
      if self.titles[0] != search_ru:
        self.titles.append(search_ru)     # добавить транслителированный вариант
    # не вручную и в наименовании был год, значит использовать его в поиске
    if search_year:
      self.year = search_year
    else:
      try:        # вручную год для поиска, взять из media.year
        self.year = int(media.year) 
      except:   pass
    if self.year < UNKNOWN_YEAR or self.year > MAX_VALID_YEAR:
      self.year = UNKNOWN_YEAR
    
  @property
  def match_type(self):
    return "New match" if self.isNewMatch else "Fix match"
  
  @property
  def search_type(self):
    return "Manual" if self.isManual else "Auto"
  
  @property
  def agent(self):
    return 'Agent.Movies' if self.isAgentMovies else 'Agent.TV_Shows'
  
  @property
  def str_titles(self):
    ''' Log(self.titles) выдаст крякозябры, а эта функция нет'''
    str_search = '[ '
    for k in self.titles:
      str_search += "'%s', " % k
    str_search = str_search[:-2]  # пару последних символов убираем
    str_search += "]"
    return str_search
 
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
        

class ejson():
  ''' Расширенный json, get'''  
  def __init__(self, json):
    self.json = json
  
  def __repr__(self):
    return self.json.__repr__()

  def __iter__(self):
    self.n = 0
    return self
  
  def __next__(self):
    if self.n <= len(self.json):
        res = self.json[self.n]
        self.n += 1
        return res
    else:
        raise StopIteration
  
  def get(self, key):
    ''' get возвращает значение ключа, либо пустой словарь, если ключа нет'''
    res = ''
    try:
      res = self.json[key]
    except:
      Log("ERROR ejson^ json[%s] = %s" % (key, res)) # type: ignore
      return res
    if res is None:
      return ''
    if isinstance(res, list): # если массив
      eres = []
      for item in res:        # каждый item - json
        eres.append(ejson(item))
      res = eres              # тогда вернём массив ejson-ов
    return res  

  def get_int(self, key):
    '''get_int возвращает целое числовое значение или 0'''       
    res = self.get(key)  
    try:
        res = int(res)
    except:
        res = 0
    return res


    
'''
md = ejson(mydata)
jd= {'nameRu': 'Джосс Уидон', 'description': None, 'posterUrl': 'https://st.kp.yandex.net/images/actor_iphone/iphone360_178.jpg', 'professionText': 'Режиссеры', 'staffId': 178, 'nameEn': 'Joss Whedon', 'professionKey': 'DIRECTOR'}
print(len(jd))
ej = ejson(jd)

for item in ej.json:
    print(item)

j0 = ejson(json_test_01)
a1 = j0.get('films')
for m in a1:
  print(m.get('nameRu'))
'''