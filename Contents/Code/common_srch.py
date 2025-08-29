# -*- coding: utf-8 -*-
# coding=utf-8
import re

from config import *  #KEYWORD_SEARCH, API_BASE_URL, UNKNOWN_YEAR, MAX_VALID_YEAR, SCORE_WEIGH_JANRE, SCORE_WEIGHT_NAME, SCORE_WEIGHT_YEAR
from debug import d, w, log_timing
from utils import AppendSearchResult, translit2ru, get_json

  
class srch_params():
  ''' Просто поскладём все параметры поиска в сюда, srch_params '''
  isAgentMovies = True    #   1. Agent.Movies или Agent.TV_Shows
  isNewMatch    = True    #   2. Определить режим - сопоставление или исправление
  isManual      = False
  titles        = []      # массив str из 1 или 2 элементов, 0-имя, 1-транскрибированное имя
  year          = 0       # год выпуска - из формы поиска
  season        = 0       # если сериал - то еще и сезон запомним
  
  def __init__(self, media, manual):
    self.isAgentMovies = False if hasattr(media, 'season') else True
    self.isNewMatch = media.filename is None
    # media.filename == None когда сопоставления еще не было, первый раз нажато "Сопоставить"
    # media.filename == filename, когда (Fix Incorrect Match), сразу будет сразу попытка поиска по media.name
    self.isManual = manual
    self.titles = []
    self.titles.append(media.name if self.isAgentMovies else media.show)    # self.titles[0]
    search_year = 0
    Log("File %s, manual = %s" % (media.name, self.isManual))    # type: ignore
    # сезон из файла пригодится в любом случае
    if not self.isAgentMovies:
      r = re.search("^(.*)\sS([0-3]\d)", self.titles[0])  # https://regex101.com/r/x53ZOY/1
      if r:
        self.season = int(r.group(2))         # S03 -> season = 3
    #if not manual:
    if not self.isManual:    
      # т.е. значение - не из строки поиска, а из media.year, media.id, media.name
      self.titles[0] = re.sub(r'_', ' ', self.titles[0])     # в наименовании _ заменяем на пробелы
      self.titles[0] = re.sub(r'\.', ' ', self.titles[0])    # in result . to ' '
      # поиск автоматический. имя выглядит как "головоломка 2 2024" или "Missiya Serenity 2005 Dlrip"
      r = re.search("^(.+)((19|20)\d\d)(.*)$", self.titles[0])  # - регексп года, , что справа отбрасывается, .
      if r:
        self.titles[0] = r.group(1).strip()   # год извлекается
        search_year = int(r.group(2))           # что слева года - имя
        Log("Regexp search_year = %s, search_title = '%s'" % (search_year, self.titles[0])) # type: ignore
      # 25 [Feature request] Сериалы. При автосопоставлении отбрасывать S0x после наименования. #25
      if not self.isAgentMovies:
        r = re.search("^(.*)\sS([0-3]\d)", self.titles[0])  # https://regex101.com/r/x53ZOY/1
        if r:
          self.titles[0] = r.group(1).strip()   #наименование без S02
          self.season = int(r.group(2))         # S03 -> season = 3
      # если имя уже русскими буквами - не добавляем ничего
      search_ru = translit2ru(self.titles[0])  # наименование часто транслитерируется англ. буквами
      if self.titles[0] != search_ru:
        self.titles.append(search_ru)     # добавить транслителированный вариант
      Log("File %s, autosearch = %s" % (media.name, search_ru)) # type: ignore
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

# log_timing funcs ------------------------------------------------------------------- 
#@log_timing  #очень много в лог    
def srch_mkres(srch, finded, results):      # >>>>>>> end::srch_mkres, duration=15
  d("\n---------------------- начинаем формировать отображение найденного")
  if len(finded['films']) == 0:
    # ничего не найдено
    return
  for i, movie in enumerate(finded['films']):
    # формирование строк меню
    id = movie["filmId"]        #MUST be
    title = ""
    if Prefs['showTypes']:                # type: ignore # Отображать тип: F:фильм, M:многосерийный, V:видео, S:сериал, T:tv-шоу
      b=''
      TypeFinded = {'FILM':'F', 'VIDEO':'V', 'TV_SERIES':'S', 'MINI_SERIES':'M', 'TV_SHOW':'T'}
      try:
        b = TypeFinded[movie['type']]     # подставить букву, соответствующую типу
      except: pass
      if b:                               # если не упал в эксепшн
         title += u"%s: " % b
    if Prefs['show2names']:             # type: ignore # "В найденных отображать и русское наименование, и английское"
      if 'nameRu' in movie:
        title += movie['nameRu']
      if len(title) > 0 and 'nameEn' in movie:
        title += '/'
      if 'nameEn' in movie:
        title += movie['nameEn']
    else:
      title = movie['nameRu'] if 'nameRu' in movie else movie['nameEn']
    if Prefs['showCountry']:             # type: ignore #"В найденных отображать страну произодства"
      if 'countries' in movie and len(movie['countries']) > 0:
        title = title + ' [%s' % movie['countries'][0]['country']
        if len(movie['countries']) > 1:
          title += ',..]'
        else:
          title += ']'
    if Prefs['showGenre']:                # type: ignore #"В найденных отображать жанр (первый, если несколько)"
      if 'genres' in movie:
        try:
          title = title + ' %s' % movie['genres'][0]['genre']
        except: pass
    if Prefs['showDescr']:                # type: ignore #"В найденных отображать первое предложение описания"
      if 'description' in movie:
        title = title + ' %s' % movie['description'].split(".")[0]
    year = int(movie['year'][:4]) if movie['year'].isdigit() else UNKNOWN_YEAR
    lang = 'ru' if 'nameRu' in movie else 'en'    # вот такой гадкий хардкод
    score = movie['score']
    d("======= %02i: %i : %s" % (i, score, title))
    AppendSearchResult(results=results,
                      id = id,
                      name = title,
                      year = year,
                      score = score,
                      lang = lang)
    

#@log_timing  #очень много в лог
def srch_and_score(srch, finded, results):
  #   1. поиск по элементам массива названий и добавление в результаты без пересечения 
  page = 1            # DO  pagination? or 20 is enouth
  finded_id = []      # список id, которые уже добавлены в match
  d("\n---------------------- начинаем find-инг: по имени [%s]" % srch.str_titles)
  for title in srch.titles:
    # формирование URL для поиска наименования фильма и запрос ejson
    resp_json = get_json(API_BASE_URL + KEYWORD_SEARCH % (String.Quote(title, True), page)) # type: ignore
    # resp_json = ejson(test_zori_json)     # 4debug
    if resp_json:
      if 'message' in resp_json:
        # Проблема: {"message":"You don't have permissions. See https://kinopoiskapiunofficial.tech"}
        AppendSearchResult(results=results, id=0, score=100, name=(u"Поиск без ключа? https://kinopoiskapiunofficial.tech"), lang='ru')
        d(u"\nsrch_and_score: Попытка поиска без ключа. %s" % resp_json["message"])
        return
    if resp_json is None:
      continue
    try:
      i = resp_json['searchFilmsCountResult']
      d(u"---- По [%s] найдено %s фильмов" % (title, i))
    except: 
      i = 0
    if 'films' in resp_json and i:
      for movie in resp_json['films']:
        if not movie['filmId'] in finded_id:  # "searchFilmsCountResult" - wonka : 18, вонка : 15
          finded_id.append(movie['filmId'])
          finded['films'].append(movie)
  d("==== Итог: %s фильмов" % len(finded['films']))  # Итого - 14

  #   2. Скоринг
  if len(finded['films']) > 0:
    d("\n---------------------- начинаем score-инг: дистанция левенштейна, год")
    for movie in finded['films']:# 
      movie['score'] = 0
      d("%s" % srch.str_titles)
      # скорининг:   по type - [ 'FILM', 'VIDEO', 'TV_SERIES', 'MINI_SERIES', 'TV_SHOW' ]
      finded_type = ''
      vscore_ratio = 0.0
      try:
        finded_type = movie['type']
      except: pass
      if srch.isAgentMovies:
        if finded_type == 'FILM':
          vscore_ratio = 1
        elif finded_type in ['TV_SHOW', 'VIDEO']:
          vscore_ratio = 0.8
        elif finded_type == 'MINI_SERIES':
          vscore_ratio = 0.3
      else:       # srch.isAgentMovies == false
        if finded_type  in ['TV_SERIES', 'MINI_SERIES']:
          vscore_ratio = 1
        elif finded_type == 'TV_SHOW':
          vscore_ratio = 0.8
      vscore = int(SCORE_WEIGH_JANRE * vscore_ratio)
      d("type score:%i %f [%s]" % (vscore, vscore_ratio, finded_type))
      movie['score'] = movie['score'] + vscore 

      # скорининг: дистанция левенштейна
      nameRu = ''
      nameEn = ''
      try:
        nameRu = movie['nameRu']
      except: pass
      try:
        nameEn = movie['nameEn']
      except: pass
      lscor = 0         # levenstain score
      # для каждого варианта написания - ищем максимальное совпадение с найденным
      for title in srch.titles:
        curr_lscor = lev_score(nameRu, nameEn, title)
        if curr_lscor > lscor:
          lscor = curr_lscor
      d("name score:%i [%s|%s]" % (lscor, nameRu, nameEn))
      movie['score'] = movie['score'] + lscor
    
      # скорининг: год
      finded_year = UNKNOWN_YEAR
      delta = -1
      try:
        finded_year = int(movie['year'][:4]) if movie['year'].isdigit() else UNKNOWN_YEAR
      except: pass
      if srch.year == UNKNOWN_YEAR or finded_year == UNKNOWN_YEAR:
        #
        yscore = int(0.8 * SCORE_WEIGHT_YEAR)
      else:
        #
        delta = abs(srch.year - finded_year)
        MAX_DELTA_YEAR = 25.0
        if delta >= MAX_DELTA_YEAR:
          yscore = 0    # too big delta
        else:
          yscore = int(SCORE_WEIGHT_YEAR * (1 - delta/MAX_DELTA_YEAR))
      d("year score:%i [%s::%s] delta=%s" % (yscore, srch.year, finded_year, delta))
      movie['score'] = movie['score'] + yscore
      d(" SUM score:%i [%s]" % (movie['score'], srch.str_titles)) 
     



# -- inner ----------------------------------------------------------------------

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