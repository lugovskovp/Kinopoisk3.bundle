# -*- coding: utf-8 -*-
# coding=utf-8
import re, datetime
from config import *        # константы
from utils import srch_params        # type: ignore # extended json и параметры поиска
from updater import Updater   

              
##################################################################
def Start():
  Log("\n\n========== START %s %s =============" % (NAME, VER)) # type: ignore 
  HTTP.CacheTime = 0                                  # type: ignore #CACHE_1HOUR
  ValidatePrefs()                 # start autoupdate
    
    
def ValidatePrefs():
  ''' This function is called when the user modifies their preferences.'''
  UpdateInterval = int(Prefs['update_interval'] or 1)*60       # type: ignore
  Chanel = Prefs['update_channel']                                # type: ignore
  Log('ValidatePrefs: update chanel=%s, interval=%i sec' % (Chanel, UpdateInterval))  # type: ignore
  if Chanel != 'none':                            # type: ignore
    Thread.CreateTimer(UpdateInterval, Updater.auto_update_thread, core=Core, pref=Prefs)  # type: ignore


##################################################################

class KinoPoiskUnoficialAgent(Agent.Movies): # type: ignore
  '''
  search
  update
  '''
  name              = '%s (%s) Movies' % (NAME, VER) 
  primary_provider  = True  # могут быть выбраны в качестве основного источника метаданных
  fallback_agent    = False # идентификатор другого агента для использования в качестве резервного
  # contributes_to идентификаторы первичных агентов, которым агент может передавать вторичные данные
  # contributes_to    = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.local', 'com.plexapp.agents.themoviedb', 'com.plexapp.agents.imdb'] 
  contributes_to    = ['com.plexapp.agents.themoviedb']
  languages         = LANGUAGES  #languages=[['ru', 'en', 'xn']]
  # accepts_from идентификаторы агентов, которые могут добавлять вторичные данные к первичным данным, предоставляемым этим агентом
  accepts_from      = ['com.plexapp.agents.localmedia'] 
  agent_type        = 'Movies'
  
     
  @log_timing
  def search(self, results, media, lang, manual=False):
  #def search(self, *args):
    ''' • self – A reference to the instance of the agent class.
        • results (ObjectContainer (page 52)) – An empty container that the developer should populate with potential matches.
        • media (Media (page 36)) – An object containing hints to be used when performing the search.
          В search media - Movie|TV_Show, а вот в update media это MediaTree 
        • lang (str - A string identifying the users currently selected language. This will be one of the constants added to the agents languages attribute.
        • manual (bool - A boolean value identifying whether the search was issued automatically during scanning, or manually by the user (in order to fix an incorrect match)  
    '''   
    #   0 - initializing search parameters
    '''if manual and not isNewMatch:
      #return   # можно автопопытку поиска отключить
      pass'''
    srch = srch_params(media, manual)
    d("\n\n========== %s.SEARCH %s, %s, %s %s start\n" % (self.name, srch.str_titles, srch.year, srch.match_type, srch.search_type))
    #   2 - MUST to have a valid token for continue
    HaveToken = APItokenRemains()
    if not HaveToken:
      Log(u">>>SEARCH STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return
    #    2 - Поиск и скоринг
    finded = {'films':[]}        # найденные 'films'
    srch_and_score(srch, finded, results)   
    #    3 - Формирование результатов для отображения (если ручной) или (найденные имена) - если автомат.
    srch_mkres(finded, results)
    d("\n>>>KinoPoisk_Movie.search END\n")

  @log_timing
  def update(self, metadata, media, lang):
    '''
    self      KinoPoiskUnnoficialAgent
    metadata  Framework.models.metadata.com_plexapp_plugins_kinopoisk3.Movie
    media     MediaTree   (search - Movie|TV_Show)
    '''
    HaveToken = APItokenRemains()
    if not HaveToken:
      Log(u">>>UPDATE STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return    
    d("\n\n ---------- %s.UPDATE start: m.id=%s tokenQuota=%s" % (self.name, metadata.id, HaveToken))
    Log("\n metadata-metadata type: %s %s " % (metadata.title, metadata.year)) # type: ignore
    # Log("\n media-MediaTree id: %s, tree: %s, name" % (media.id, media.tree, media.name))

    valid_posters = []
    valid_poster0 = []
    valid_arts = []   
    media.thumb = ""
    @parallelize    # type: ignore # load_gallery posters, duration=3523, load_gallery arts, duration=4383, update, duration=4389
    def parallel_update():
      # постеры и галерею - самыми первыми: они самые долгие
      @task # type: ignore
      def upd_posters(metadata=metadata, valid_posters = valid_posters):
        load_gallery(metadata, valid_posters, IsNeedPosters=True)  # 'POSTER'
      @task # type: ignore
      def upd_arts(metadata=metadata):
        load_gallery(metadata, valid_arts, IsNeedPosters=False)  #  'WALLPAPER'
        pass
      @task # type: ignore
      def upd_staff(metadata=metadata):
        load_staff(metadata)
      @task # type: ignore
      def upd_reviews(metadata=metadata):    
        load_reviews(metadata)
      @task # type: ignore
      def upd_meta(metadata=metadata):
        load_metadata(metadata, valid_poster0)
        media.title = metadata.title        # в media - надо вернуть наименование выбранного фильма - заменив текущее из поиска
      @task # type: ignore
      def upd_distribution(metadata=metadata):
        load_distribution(metadata)
    # параллельная работа окончена, все задачи завершены
    valid_names = valid_poster0 + valid_posters
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_arts)
    if len(valid_names) > 0:
      media.thumb = valid_names[0]
    d(" ************* KinoPoiskUnnoficialAgent.UPDATE.end\n")


class KinoPoiskUnoficialAgent(Agent.TV_Shows): # type: ignore
  name              = '%s (%s) Serials' % (NAME, VER) 
  primary_provider  = True 
  fallback_agent    = False 
  # contributes_to    = ['com.plexapp.plugins.kinopoisk3', 'com.plexapp.agents.local', 'com.plexapp.agents.themoviedb', 'com.plexapp.agents.imdb'] 
  languages         = LANGUAGES  #languages=['ru', 'en', 'xn']
  #accepts_from      = ['com.plexapp.agents.localmedia'] 
  agent_type        = 'TV_Shows'


  @log_timing  
  def search(self, results, media, lang, manual=False):
    #   1 - initializing search parameters
    srch = srch_params(media, manual)
    d("\n\n========== %s.SEARCH %s, %s, %s %s start\n" % (self.name, srch.str_titles, srch.year, srch.match_type, srch.search_type))
    finded = {'films':[]}        # найденные 'films'
    #   2 - MUST to have a valid token for continue
    HaveToken = APItokenRemains()
    if not HaveToken:
      Log(u">>>SEARCH STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return
    #
    srch_and_score(srch, finded, results) 
    srch_mkres(finded, results)
    d("\n>>>KinoPoisk_TV_Show.search %s %s END\n" % (srch.str_titles, srch.year))


  @log_timing  
  def update(self, metadata, media, lang):
    # В search media - Movie|TV_Show, а вот в update media это Framework.api.agentkit.MediaTree
    '''
    Framework.api.agentkit.MediaTree 
      [] Framework.api.agentkit.MediaPart
    '''
    HaveToken = APItokenRemains()
    if not HaveToken:
      Log(u">>>UPDATE STOPPED: has no valid key or not remains daily attempts")                  # type: ignore
      return
    d("\n\n ---------- %s.UPDATE start: m.id=%s tokenQuota=%s" % (self.name, metadata.id, HaveToken))
    d( 'media.all_parts parts: %s' % media.all_parts()[0] )     # MediaPart
    # 'MediaPart' object has no attribute  filename name path
    d( 'media.all_parts[0] size: %s' % media.all_parts()[0] )
    d( 'media.all_parts[0] size: %s' % media.all_parts()[0].size )
    d( 'media.all_parts seasons: %s' % media.seasons ) 
    valid_posters = []
    valid_poster0 = []
    valid_arts = []   
    media.thumb = ""

    @parallelize    # type: ignore # load_gallery posters, duration=3523, load_gallery arts, duration=4383, update, duration=4389
    def parallel_update():
      # постеры и галерею - самыми первыми: они самые долгие
      @task # type: ignore
      def upd_posters(metadata=metadata, valid_posters = valid_posters):
        load_gallery(metadata, valid_posters, IsNeedPosters=True)  # 'POSTER'
      @task # type: ignore
      def upd_arts(metadata=metadata):
        load_gallery(metadata, valid_arts, IsNeedPosters=False)  #  'WALLPAPER'
        pass
      @task # type: ignore
      def upd_staff(metadata=metadata):
        load_staff(metadata)
      @task # type: ignore
      def upd_reviews(metadata=metadata):    
        load_reviews(metadata)
      @task # type: ignore
      def upd_meta(metadata=metadata):
        load_metadata(metadata, valid_poster0)
        '''if hasattr(media, 'show'):     # в media - надо вернуть наименование выбранного фильма - заменив текущее из поиска
          media.show = metadata.title
        else:
          media.name = metadata.title'''
        media.title = metadata.title        # в media - надо вернуть наименование выбранного фильма - заменив текущее из поиска
      @task # type: ignore
      def upd_episodes(metadata=metadata):
        load_episodes(metadata, media)
    # параллельная работа окончена, все задачи завершены
    valid_names = valid_poster0 + valid_posters
    #metadata.posters.validate_keys(valid_names)
    #metadata.art.validate_keys(valid_arts)
    media.thumb = valid_names[0]
    
  


# ========================================================================

def AppendSearchResult(results, id, name=None, year=-1, score=0, lang=None):
  # Добавить к результату(там) поиска еще один результат
  new_result = dict(id=str(id), name=name, year=int(year), score=score, lang=lang)
  if isinstance(results, list):
      results.append(new_result)
  else:
      results.Append(MetadataSearchResult(**new_result)) # type: ignore
  return


@log_timing
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
     

#@log_timing      
def srch_mkres(finded, results):      # >>>>>>> end::srch_mkres, duration=15
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
      TypeFinded = {'FILM':'F', 'VIDEO':'V', 'TV_SERIES':'S', 'MINI_SERIES':'M', 'TV_SHOW':'s'}
      try:
        b = TypeFinded[movie['type']]     # подставить букву, соответствующую типу
      except: pass
      if b:                               # если не упал в эксепшн
         title += u"%s: " % b
    if Prefs['show2names']:             # type: ignore #"В найденных отображать и русское наименование, и английское"
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

       
@log_timing  
def load_metadata(metadata, valid_names):
  #
  d("-------------------update:load_metadata id=%s title=%s" % (metadata.id, metadata.title))
  #msStart = getMilliseconds(Datetime.Now())
  isAgentMovies = False if hasattr(metadata, 'seasons') else True
  
  movie_data = get_json(API_BASE_URL + FILM_DETAILS % metadata.id)
  if not movie_data or not metadata.id:
    return
  # TODO добавить   "imdbId": "tt0379786",

  #   title                     = Template.String()
  repls = (u' (видео)', u' (ТВ)', u' (мини-сериал)', u' (сериал)')
  title = reduce(lambda a, kv: a.replace(kv, ''), repls, movie_data.get('nameRu')) # type: ignore
  metadata.title = title

  if isAgentMovies:
    #   year                      = Template.Integer()
    if movie_data.get('year'):
      metadata.year = int(movie_data.get('year'))
    else:
      metadata.year = ''
    if metadata.year == 0:
      metadata.year = ''
    
    #   originally_available_at   = Template.Date()   A dateobject specifying the movie’s original release date.
    #   tagline                   = Template.String()
    metadata.tagline = movie_data.get('slogan')
    
  #   summary                   = Template.String()
  summary_add = ''
  # "Описание: отображать слоган фильма"
  if Prefs['desc_show_slogan']: # type: ignore
    val = movie_data.get('shortDescription')
    if val:
      summary_add += "%s\n" % val
      d(u"   Девиз = %s" % summary_add)
  #  "Описание: отображать рейтинг Кинопоиск"
  if Prefs['desc_rating_kp']: # type: ignore
    val = movie_data.get('ratingKinopoisk')
    if val:
      summary_add += u'КиноПоиск: %s' % val
      val1 = movie_data.get('ratingKinopoiskVoteCount')
      if val1:
        summary_add += ' (%s)' % val1
      d(u"   'КиноПоиск: %s(%s) " % (val, val1))
      summary_add += '\n'
  # "Описание: отображать рейтинг IMDB"
  if Prefs['desc_rating_imdb']: # type: ignore
    val = movie_data.get('ratingImdb')
    if val:
      summary_add += u'IMDB: %s' % val
      val1 = movie_data.get('ratingImdbVoteCount')
      if val1:
        summary_add += ' (%s)' % val1
      summary_add += '\n'
  #
  try:
    summary_add += movie_data.get('description')
  except:  pass
  metadata.summary = summary_add
  
  ## rating     A float between 0 and 10 specifying the movie’s rating.
  metadata.rating = 0.0
  try:
    metadata.rating = float(movie_data.get('ratingImdb'))
  except:  pass
  if metadata.rating == 0:
    try:
      metadata.rating = float('ratingKinopoisk')
    except:  pass 

  #   trivia                    = Template.String()   A string containing trivia about the movie.
  #   quotes                    = Template.String()
  #   content_rating            = Template.String()
  val = movie_data.get('ratingMpaa')
  if val:
    metadata.content_rating = val.upper()
  else:
    val = movie_data.get('ratingAgeLimits')
    metadata.content_rating = val
  #   content_rating_age        = Template.Integer()
  try:
    metadata.content_rating_age = int(movie_data.get('ratingAgeLimits').replace('age', '') or 0)
  except:  pass
  #   countries                 = Template.Set(Template.String())
  countries = []
  for country in movie_data.get('countries'):
    countries.append(country.get('country'))
  metadata.countries = countries
  
  #   chapters                  = Template.Set(Chapter()) 
  ##  original_title       A string specifying the movie’s original title.
  val = movie_data.get('nameOriginal') 
  metadata.original_title = val if val else movie_data.get('nameEn')
  
  ## genres        A set of strings specifying the movie’s genre  
  genres = []
  for genre in movie_data.get('genres'):
      genres.append(genre.get('genre'))
  metadata.genres = genres       
  
  ## posters     A container of proxy objects representing the movie’s posters. See below for information about proxy objects.
  
  try:
    d("   === load meta start posterUrlPreview %s" % movie_data.get('posterUrlPreview'))
    #c "c:\Users\plugo\AppData\Local\Plex Media Server\Plug-ins\MoviePosterDB.bundle\Contents\Code\__init__.py" 
    image_url = movie_data.get('posterUrl')
    thumb_url = movie_data.get('posterUrlPreview')
    #metadata.posters[image_url] = Proxy.Preview(HTTP.Request(thumb_url), sort_order=0)
    metadata.posters[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order=0) # type: ignore
    valid_names.append(image_url)
    #metadata.posters.validate_keys(valid_names)  #только после ВСЕХ posters
  except:    pass
  # d("===================update:load_meta end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))
  ## themes    A container of proxy objects representing the movie’s theme music. 


@log_timing
def load_episodes(metadata, media):
  seasons_json = get_json(API_BASE_URL + SERIAL_SEASONS % metadata.id)
  #seasons_json = get_json(API_BASE_URL + SERIAL_SEASONS % 464963)   # 464963 - Игра престолов
  if not seasons_json:
    return
  if 'message' in seasons_json:
    d(u"\nsrch_and_score: Попытка поиска без ключа. %s" % seasons_json["message"])
    return
  #seasons_qty = seasons_json.get('total')
  for season_num, season_data in enumerate(seasons_json.get('items'), 1):    # 1,2...
    if season_num not in media.seasons:      
      continue
    # отлично, есть локальные файлы из сезонов из найденного сезона
    for episode_num, episode_data in enumerate(season_data.get('episodes'), 1):
      # по каждой серии
      s_num = episode_data.get('seasonNumber')
      e_num = episode_data.get('episodeNumber')
      episode = metadata.seasons[s_num].episodes[e_num]
      episode.title = ''
      episode.originally_available_at = None
      episode.summary = ''
      #
      title = episode_data.get('nameRu') 
      if not title:
        title = ''
      titleE = episode_data.get('nameEn')
      if not titleE:
        titleE = ''
      else:
        if title:
          title = title + ' / '
      episode.title = title + titleE
      dat = episode_data.get('releaseDate')
      if dat:
        episode.originally_available_at = datetime.datetime.strptime(dat, "%Y-%m-%d").date()
      episode.summary = episode_data.get('synopsis')
      d("%s:%s %s  %s" % (season_num, episode_num, dat, episode.title))

    
@log_timing  
def load_distribution(metadata):
  #https://www.kinopoisk.ru/film/5405057/studio/
  # d("-------------------update:load_distribution - start")
  ## msStart = getMilliseconds(Datetime.Now())
  movie_data = get_json(API_BASE_URL + FILM_DISTRIBUTION % metadata.id).get('items')
  if not movie_data:
    return
  #[ LOCAL, COUNTRY_SPECIFIC, PREMIERE, ALL, WORLD_PREMIER ], subType : [ CINEMA, DVD, DIGITAL, BLURAY ] 
  for data in movie_data:
    if data.get('type') == 'ALL':
      metadata.originally_available_at = Datetime.ParseDate((data.get('date')).replace('00.', '01.'), '%Y-%m-%d').date()  # type: ignore
      #   studio                    = Template.String() A string specifying the movie’s studio.
      for comp in data.get('companies'):
        metadata.studio = comp.get('name')  # so, only last like highlander  1981-12-02  Studio updated
  # d("===================update:load_distribution end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))
    
  
#@log_timing  
def load_staff(metadata):
  ''' - штат - актеры, сценаристы, режиссер '''
  #d("-------------------update:load_staff - start")
  #msStart = getMilliseconds(Datetime.Now())  # '2025-01-25 12:41:53.921000' 
  isAgentMovies = False if hasattr(metadata, 'seasons') else True
  staff_data = get_json(API_BASE_URL + FILM_STAFF % metadata.id)
  if not staff_data:
    return
  # d("%s" % staff_data) # там сразу массив, без ключа
  # professionKey = [ WRITER, OPERATOR, EDITOR, COMPOSER, PRODUCER_USSR, HIMSELF, HERSELF, 
  # HRONO_TITR_MALE, HRONO_TITR_FEMALE, TRANSLATOR, DIRECTOR, DESIGN, PRODUCER, ACTOR, VOICE_DIRECTOR, UNKNOWN ]
  #   writers                   = Template.Set(Person())
  #   directors                 = Template.Set(Person())
  #   producers                 = Template.Set(Person())
  #   roles                     = Template.Set(Person())    TV_Show - only role
  
  @parallelize  # type: ignore
  def upd_staff():
    if isAgentMovies:
      metadata.directors.clear()
      metadata.producers.clear()
      metadata.writers.clear()
    metadata.roles.clear()
    for member in staff_data:
      #
      @task # type: ignore
      def upd_member(metadata = metadata,
                     member = member):
        prof = member.get('professionKey')
        name = member.get('nameRu') if member.get('nameRu') else member.get('nameEn')
        url = member.get('posterUrl')
        role_description = member.get('description')
        if prof == 'DIRECTOR' and isAgentMovies:
          if name:
            director = metadata.directors.new()
            director.name = name
            if url:
              director.photo = url
        if prof == 'PRODUCER' and isAgentMovies:
          if name:
            producer = metadata.producers.new()
            producer.name = name
            if url:
              producer.photo = url
        if prof == 'WRITER' and isAgentMovies:
          if name:
            writer = metadata.writers.new()
            writer.name = name
            if url:
              writer.photo = url
        if prof == 'ACTOR':
          if name and role_description:
            role = metadata.roles.new()
            role.name = name
            role.role = role_description
            if url:
              role.photo = url  
        #d("   staff %s = %s (%s)" % (prof, name, role_description))
  # d("===================update:load_staff end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))
   
    
@log_timing   
def load_reviews(metadata):
  ''' обзоры с кинопоиска '''
  #d("-------------------update:load_reviews - start")
  #msStart = getMilliseconds(Datetime.Now())  # '2025-01-25 12:41:53.921000' 
  reviews_dict = get_json(API_BASE_URL + FILM_REVIEW % metadata.id)
  if not reviews_dict:
    return            # нечего время терять
  @parallelize  # type: ignore
  def upd_reviews():
    metadata.reviews.clear()
    for item in reviews_dict.get('items'):
      @task # type: ignore
      def add_review(item = item,
                     metadata = metadata):
        author = u"%s +%s|-%s" % (item.get('author'), int(item.get('positiveRating')), int(item.get('negativeRating')))
        #author = u"%s +%s|-%s" % (item.get('author'), item.get_int('positiveRating'), item.get_int('negativeRating'))
        source = item.get('title') if item.get('title') else 'Кинопоиск'   # везде "Кинопоиск" - скучно, "title": "Королевский шпион, Часть 18.",
        text = re.sub(r'<("[^"]*"|\'[^\']*\'|[^\'">])*>', '', item.get('description'))   # вырезать теги
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e]', '', text)
        if author and source and text:
          review = metadata.reviews.new()
          review.author = author
          review.source = source
          review.image = 'rottentomatoes://image.review.rotten' if item.get('type') == "POSITIVE" else 'rottentomatoes://image.review.fresh'
          review.text = text
    ''' not used:
    "kinopoiskId": 1814200,
    "date": "2013-06-21T14:27:26",
  
  '''
  #d("===================update:load_reviews end, Duration=%s\n"  % (getMilliseconds(Datetime.Now()) - msStart))

  
@log_timing  
def load_gallery(metadata, valid_names, IsNeedPosters = True):
  ''' IsNeedPoster - постеры (false - artworks)
  metadata
  valid_names - массив проксимедиа с изображениями
  IsNeedPosters загружать постеры (иначе - обои)
  '''
  ## art       A container of proxy objects representing the movie’s background art. 
  def load_dict(type_artwork):
    '''   STILL - кадры
          SHOOTING - изображения со съемок
          POSTER - постеры
          FAN_ART - фан-арты
          PROMO - промо
          CONCEPT - концепт-арты
          WALLPAPER - обои
          COVER - обложки
          SCREENSHOT - скриншоты
    ''' 
    res = get_json(API_BASE_URL + FILM_POSTERS % (metadata.id, type_artwork))
    d("load_gallery:load_dict %s, finded [%s] results" % (type_artwork, res.get('total')))
    if not 'total' in res:
      res['total'] = 0
    return res
    
  if IsNeedPosters:    # posters - картинка на странице о фильме и в библиотеке
    art_dict = load_dict('POSTER') 
    if art_dict['total'] == 0:
      #тут нет постеров, ну вообще нет
      d("load_gallery: nothing %s finded")
      return
  else:               # грузим картинки для заднего фона страницы       
    art_dict = load_dict('WALLPAPER') 
    if art_dict['total'] == 0:
      art_dict = load_dict('COVER') 
      if art_dict['total'] == 0:
        art_dict = load_dict('PROMO')
        if art_dict['total'] == 0:
          art_dict = load_dict('STILL')
          if art_dict['total'] == 0:
            #тут рыбы нет, ну вообще нет
            d("load_gallery: nothing %s finded")
            return

  d("film='%s' id = %s, find total: %s" % (metadata.title, metadata.id, art_dict['total']))  
  #valid_names = []
  @parallelize   # type: ignore
  def upd_posters():
    pref_max = int(Prefs['poster_limit'])         # type: ignore
    max_posters = pref_max if pref_max else 30    # ну вот захардкодил 30 как 'очень много'
    for i, mov in enumerate(art_dict.get('items')):
      image_url = mov.get('imageUrl')
      thumb_url = mov.get('previewUrl')
      @task  # type: ignore # Create a task for updating poster
      def upd_poster( i=i, 
                      image_url=image_url, 
                      thumb_url=thumb_url, 
                      metadata=metadata,
                      valid_names=valid_names,
                      max_posters = max_posters):
        if i >= max_posters:
          #d("max posters = %s" % max_posters)
          return
        # d(" << @task:%02i:load_gallery:start %s  %s" % (i,('poster' if IsNeedPosters else 'art'), thumb_url))
        #metadata.posters[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order = i+1)
        if IsNeedPosters:
          # sort_order=i+1 т.к. № 0 - в upd_metadata
          metadata.posters[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order=i+1) # type: ignore
        else:
          # art or banners
          metadata.art[image_url] = Proxy.Preview(requests.get(thumb_url).content, sort_order=i) # type: ignore
        valid_names.append(image_url)
        # d(" ** @task:%02i:load_gallery:e  %s=%s" % (i,('poster' if IsNeedPosters else 'art'), thumb_url))
  '''
  # валидейт - все картинки привязывает в метадату. Надо за раз - и постеры и обои, при пересечении печаль
  if IsNeedPosters:
    metadata.posters.validate_keys(valid_names)
  else:
    metadata.art.validate_keys(valid_names)'''
  # d("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n %s" % valid_names)


'''
    def load_seasons(self, metadata, media):
        # https://kinopoiskapiunofficial.tech/documentation/api/#/films/get_api_v2_2_films__id_ 
        # GET /api/v2.2/films/{id}/seasons

        self.l('---------------------------load series from kinopoisk')
        seasons = self.make_request(self.conf.api.seasons, metadata['id'])
        if not seasons:
            return

    
    def load_series(self, metadata, media):
        self.l('load series from kinopoisk')
'''